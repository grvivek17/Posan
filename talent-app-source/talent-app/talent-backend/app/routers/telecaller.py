import json
import os
import logging
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
import aiosqlite

from app.database import get_db
from app.ai_helper import generate_telecaller_script
from app.twilio_service import (
    is_twilio_configured,
    make_call,
    build_questions_twiml,
    build_next_question_twiml,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/telecaller", tags=["telecaller"])


class QuestionCreate(BaseModel):
    requirement_id: Optional[int] = None
    question: str
    question_order: Optional[int] = 0


class CallCreate(BaseModel):
    profile_id: int
    requirement_id: Optional[int] = None


class TwilioCallCreate(BaseModel):
    profile_id: int
    requirement_id: Optional[int] = None
    phone_number: str


class ResponseCreate(BaseModel):
    call_id: int
    question_id: int
    response: str


class BulkResponseCreate(BaseModel):
    call_id: int
    responses: list[dict]


@router.get("/twilio-status")
async def twilio_status():
    return {"configured": is_twilio_configured()}


@router.post("/questions")
async def create_question(q: QuestionCreate, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute(
        "INSERT INTO telecaller_questions (requirement_id, question, question_order) VALUES (?, ?, ?)",
        (q.requirement_id, q.question, q.question_order)
    )
    await db.commit()
    return {"id": cursor.lastrowid, "question": q.question, "requirement_id": q.requirement_id, "question_order": q.question_order}


@router.get("/questions")
async def list_questions(requirement_id: Optional[int] = None, db: aiosqlite.Connection = Depends(get_db)):
    if requirement_id:
        cursor = await db.execute(
            "SELECT * FROM telecaller_questions WHERE requirement_id = ? ORDER BY question_order",
            (requirement_id,)
        )
    else:
        cursor = await db.execute("SELECT * FROM telecaller_questions ORDER BY question_order")
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


@router.delete("/questions/{question_id}")
async def delete_question(question_id: int, db: aiosqlite.Connection = Depends(get_db)):
    await db.execute("DELETE FROM telecaller_questions WHERE id = ?", (question_id,))
    await db.commit()
    return {"message": "Question deleted"}


@router.post("/calls")
async def create_call(call: CallCreate, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM profiles WHERE id = ?", (call.profile_id,))
    profile = await cursor.fetchone()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    cursor = await db.execute(
        "INSERT INTO telecaller_calls (profile_id, requirement_id, status) VALUES (?, ?, 'in_progress')",
        (call.profile_id, call.requirement_id)
    )
    await db.commit()
    call_id = cursor.lastrowid
    if call.requirement_id:
        q_cursor = await db.execute(
            "SELECT * FROM telecaller_questions WHERE requirement_id = ? ORDER BY question_order",
            (call.requirement_id,)
        )
    else:
        q_cursor = await db.execute("SELECT * FROM telecaller_questions ORDER BY question_order")
    questions = [dict(row) for row in await q_cursor.fetchall()]
    profile_dict = dict(profile)
    skills = {}
    if profile_dict.get("skills_json"):
        try:
            skills = json.loads(profile_dict["skills_json"])
        except json.JSONDecodeError:
            pass
    question_texts = [q["question"] for q in questions]
    script = await generate_telecaller_script(question_texts, {"name": profile_dict["name"], "skills": skills})
    return {
        "call_id": call_id,
        "profile": {"id": profile_dict["id"], "name": profile_dict["name"], "email": profile_dict["email"], "phone": profile_dict["phone"]},
        "questions": questions,
        "script": script,
    }


# --- Calls (Twilio - automated flow) ---
@router.post("/calls/twilio")
async def create_twilio_call(
    call: TwilioCallCreate,
    request: Request,
    db: aiosqlite.Connection = Depends(get_db),
):
    """Initiate a real phone call via Twilio with automated TTS questions."""
    if not is_twilio_configured():
        raise HTTPException(
            status_code=503,
            detail="Twilio is not configured. Set TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, and TWILIO_PHONE_NUMBER.",
        )

    cursor = await db.execute("SELECT * FROM profiles WHERE id = ?", (call.profile_id,))
    profile = await cursor.fetchone()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile_dict = dict(profile)

    if call.requirement_id:
        q_cursor = await db.execute(
            "SELECT * FROM telecaller_questions WHERE requirement_id = ? ORDER BY question_order",
            (call.requirement_id,)
        )
    else:
        q_cursor = await db.execute("SELECT * FROM telecaller_questions ORDER BY question_order")
    questions = [dict(row) for row in await q_cursor.fetchall()]

    if not questions:
        raise HTTPException(status_code=400, detail="No screening questions found. Add questions first.")

    question_texts = [q["question"] for q in questions]
    question_ids = [q["id"] for q in questions]

    cursor = await db.execute(
        """INSERT INTO telecaller_calls
           (profile_id, requirement_id, status, phone_number, questions_json)
           VALUES (?, ?, 'calling', ?, ?)""",
        (call.profile_id, call.requirement_id, call.phone_number,
         json.dumps({"texts": question_texts, "ids": question_ids}))
    )
    await db.commit()
    call_db_id = cursor.lastrowid

    base_url = os.getenv("BACKEND_URL", "").rstrip("/")
    if not base_url:
        base_url = str(request.base_url).rstrip("/")

    twiml_url = f"{base_url}/api/telecaller/twilio/twiml/{call_db_id}/start"

    try:
        result = make_call(to_number=call.phone_number, twiml_url=twiml_url)
    except Exception as e:
        await db.execute(
            "UPDATE telecaller_calls SET status = 'failed' WHERE id = ?",
            (call_db_id,)
        )
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Failed to initiate call: {str(e)}")

    if result:
        await db.execute(
            "UPDATE telecaller_calls SET twilio_sid = ?, twilio_status = ? WHERE id = ?",
            (result["call_sid"], result["status"], call_db_id)
        )
        await db.commit()

    return {
        "call_id": call_db_id,
        "twilio_sid": result["call_sid"] if result else None,
        "status": "calling",
        "profile": {
            "id": profile_dict["id"],
            "name": profile_dict["name"],
            "email": profile_dict["email"],
            "phone": profile_dict["phone"],
        },
        "phone_number": call.phone_number,
        "questions_count": len(questions),
    }


# --- Twilio Webhooks ---
@router.post("/twilio/twiml/{call_db_id}/start")
@router.get("/twilio/twiml/{call_db_id}/start")
async def twilio_twiml_start(call_db_id: int, db: aiosqlite.Connection = Depends(get_db)):
    """Twilio webhook: returns initial TwiML with greeting and first question."""
    cursor = await db.execute(
        "SELECT c.*, p.name as profile_name FROM telecaller_calls c JOIN profiles p ON c.profile_id = p.id WHERE c.id = ?",
        (call_db_id,)
    )
    call_row = await cursor.fetchone()
    if not call_row:
        return Response(content="<Response><Say>Error. Call not found.</Say><Hangup/></Response>",
                        media_type="text/xml")

    call_dict = dict(call_row)
    questions_data = json.loads(call_dict.get("questions_json") or "{}")
    question_texts = questions_data.get("texts", [])

    base_url = os.getenv("BACKEND_URL", "").rstrip("/")
    if not base_url:
        base_url = "https://app-ectnjehb.fly.dev"

    twiml = build_questions_twiml(
        questions=question_texts,
        candidate_name=call_dict["profile_name"],
        base_url=base_url,
        call_db_id=call_db_id,
    )

    await db.execute("UPDATE telecaller_calls SET status = 'in_progress' WHERE id = ?", (call_db_id,))
    await db.commit()

    return Response(content=twiml, media_type="text/xml")


@router.post("/twilio/twiml/{call_db_id}/{question_index}")
@router.get("/twilio/twiml/{call_db_id}/{question_index}")
async def twilio_twiml_question(
    call_db_id: int,
    question_index: int,
    db: aiosqlite.Connection = Depends(get_db),
):
    """Twilio webhook: returns TwiML for a specific question (used for retries)."""
    cursor = await db.execute("SELECT questions_json FROM telecaller_calls WHERE id = ?", (call_db_id,))
    call_row = await cursor.fetchone()
    if not call_row:
        return Response(content="<Response><Say>Error.</Say><Hangup/></Response>", media_type="text/xml")

    questions_data = json.loads(dict(call_row).get("questions_json") or "{}")
    question_texts = questions_data.get("texts", [])

    base_url = os.getenv("BACKEND_URL", "").rstrip("/")
    if not base_url:
        base_url = "https://app-ectnjehb.fly.dev"

    twiml = build_next_question_twiml(
        questions=question_texts,
        question_index=question_index,
        base_url=base_url,
        call_db_id=call_db_id,
    )
    return Response(content=twiml, media_type="text/xml")


@router.post("/twilio/gather/{call_db_id}/{question_index}")
async def twilio_gather_response(
    call_db_id: int,
    question_index: int,
    request: Request,
    db: aiosqlite.Connection = Depends(get_db),
):
    """Twilio webhook: receives speech response and moves to next question."""
    form_data = await request.form()
    speech_result = form_data.get("SpeechResult", "")
    confidence = form_data.get("Confidence", "0")

    logger.info(f"Call {call_db_id}, Q{question_index}: speech='{speech_result}', confidence={confidence}")

    cursor = await db.execute("SELECT questions_json FROM telecaller_calls WHERE id = ?", (call_db_id,))
    call_row = await cursor.fetchone()
    if not call_row:
        return Response(content="<Response><Say>Error.</Say><Hangup/></Response>", media_type="text/xml")

    questions_data = json.loads(dict(call_row).get("questions_json") or "{}")
    question_texts = questions_data.get("texts", [])
    question_ids = questions_data.get("ids", [])

    if question_index < len(question_ids):
        q_id = question_ids[question_index]
        await db.execute(
            "INSERT INTO telecaller_responses (call_id, question_id, response) VALUES (?, ?, ?)",
            (call_db_id, q_id, f"{speech_result} (confidence: {confidence})")
        )
        await db.commit()

    next_index = question_index + 1

    base_url = os.getenv("BACKEND_URL", "").rstrip("/")
    if not base_url:
        base_url = "https://app-ectnjehb.fly.dev"

    if next_index >= len(question_texts):
        await db.execute(
            "UPDATE telecaller_calls SET status = 'completed' WHERE id = ?",
            (call_db_id,)
        )
        await db.commit()

    twiml = build_next_question_twiml(
        questions=question_texts,
        question_index=next_index,
        base_url=base_url,
        call_db_id=call_db_id,
    )
    return Response(content=twiml, media_type="text/xml")


@router.post("/twilio/status/{call_db_id}")
async def twilio_status_callback(
    call_db_id: int,
    request: Request,
    db: aiosqlite.Connection = Depends(get_db),
):
    """Twilio webhook: receives call status updates."""
    form_data = await request.form()
    call_status = form_data.get("CallStatus", "")
    call_duration = form_data.get("CallDuration", "0")
    recording_url = form_data.get("RecordingUrl", "")

    logger.info(f"Call {call_db_id} status update: {call_status}, duration: {call_duration}")

    updates = ["twilio_status = ?"]
    values: list = [call_status]

    if call_duration and call_duration != "0":
        updates.append("call_duration = ?")
        values.append(int(call_duration))

    if recording_url:
        updates.append("recording_url = ?")
        values.append(recording_url)

    if call_status in ("completed", "busy", "no-answer", "canceled", "failed"):
        updates.append("status = ?")
        if call_status == "completed":
            values.append("completed")
        else:
            values.append(f"failed ({call_status})")

    values.append(call_db_id)
    await db.execute(
        f"UPDATE telecaller_calls SET {', '.join(updates)} WHERE id = ?",
        tuple(values)
    )
    await db.commit()

    return Response(content="<Response/>", media_type="text/xml")


# --- Call Status Polling ---
@router.get("/calls/{call_id}/status")
async def get_call_live_status(call_id: int, db: aiosqlite.Connection = Depends(get_db)):
    """Poll the current status of a call (for frontend updates)."""
    cursor = await db.execute(
        """SELECT c.id, c.status, c.twilio_sid, c.twilio_status, c.call_duration,
                  c.recording_url, c.phone_number, p.name as profile_name
           FROM telecaller_calls c
           JOIN profiles p ON c.profile_id = p.id
           WHERE c.id = ?""",
        (call_id,)
    )
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Call not found")

    result = dict(row)

    r_cursor = await db.execute("""
        SELECT r.*, q.question
        FROM telecaller_responses r
        JOIN telecaller_questions q ON r.question_id = q.id
        WHERE r.call_id = ?
    """, (call_id,))
    result["responses"] = [dict(r) for r in await r_cursor.fetchall()]

    return result


@router.get("/calls")
async def list_calls(db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("""
        SELECT c.*, p.name as profile_name, p.email as profile_email, p.phone as profile_phone
        FROM telecaller_calls c
        JOIN profiles p ON c.profile_id = p.id
        ORDER BY c.created_at DESC
    """)
    rows = await cursor.fetchall()
    calls = []
    for row in rows:
        call_item = dict(row)
        r_cursor = await db.execute("""
            SELECT r.*, q.question
            FROM telecaller_responses r
            JOIN telecaller_questions q ON r.question_id = q.id
            WHERE r.call_id = ?
        """, (call_item["id"],))
        call_item["responses"] = [dict(r) for r in await r_cursor.fetchall()]
        calls.append(call_item)
    return calls


@router.get("/calls/{call_id}")
async def get_call(call_id: int, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("""
        SELECT c.*, p.name as profile_name, p.email as profile_email, p.phone as profile_phone
        FROM telecaller_calls c
        JOIN profiles p ON c.profile_id = p.id
        WHERE c.id = ?
    """, (call_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Call not found")
    call_item = dict(row)

    r_cursor = await db.execute("""
        SELECT r.*, q.question
        FROM telecaller_responses r
        JOIN telecaller_questions q ON r.question_id = q.id
        WHERE r.call_id = ?
    """, (call_id,))
    call_item["responses"] = [dict(r) for r in await r_cursor.fetchall()]
    return call_item


# --- Responses ---
@router.post("/responses")
async def submit_response(resp: ResponseCreate, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute(
        "INSERT INTO telecaller_responses (call_id, question_id, response) VALUES (?, ?, ?)",
        (resp.call_id, resp.question_id, resp.response)
    )
    await db.commit()
    return {"id": cursor.lastrowid, "call_id": resp.call_id, "question_id": resp.question_id, "response": resp.response}


@router.post("/responses/bulk")
async def submit_bulk_responses(bulk: BulkResponseCreate, db: aiosqlite.Connection = Depends(get_db)):
    results = []
    for item in bulk.responses:
        cursor = await db.execute(
            "INSERT INTO telecaller_responses (call_id, question_id, response) VALUES (?, ?, ?)",
            (bulk.call_id, item["question_id"], item["response"])
        )
        results.append({"id": cursor.lastrowid, "question_id": item["question_id"], "response": item["response"]})
    await db.execute("UPDATE telecaller_calls SET status = 'completed' WHERE id = ?", (bulk.call_id,))
    await db.commit()
    return {"call_id": bulk.call_id, "status": "completed", "responses": results}


@router.put("/calls/{call_id}/complete")
async def complete_call(call_id: int, db: aiosqlite.Connection = Depends(get_db)):
    await db.execute("UPDATE telecaller_calls SET status = 'completed' WHERE id = ?", (call_id,))
    await db.commit()
    return {"message": "Call marked as completed"}

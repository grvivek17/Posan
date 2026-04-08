import json
import logging
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
import aiosqlite

from app.database import get_db
from app.vector_store import semantic_search

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/requirements", tags=["requirements"])


class RequirementCreate(BaseModel):
    title: str
    description: Optional[str] = ""
    skills_needed: Optional[str] = ""
    team_size: Optional[int] = 1
    status: Optional[str] = "open"


class RequirementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    skills_needed: Optional[str] = None
    team_size: Optional[int] = None
    status: Optional[str] = None


async def _generate_req_code(db: aiosqlite.Connection) -> str:
    """Generate the next requirement code like REQ-001, REQ-002, etc."""
    cursor = await db.execute("SELECT COUNT(*) as cnt FROM requirements")
    row = await cursor.fetchone()
    count = row["cnt"] if row else 0
    return f"REQ-{count + 1:03d}"


@router.post("/")
async def create_requirement(req: RequirementCreate, db: aiosqlite.Connection = Depends(get_db)):
    req_code = await _generate_req_code(db)
    cursor = await db.execute(
        """INSERT INTO requirements (title, description, skills_needed, team_size, status, req_code)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (req.title, req.description, req.skills_needed, req.team_size, req.status, req_code)
    )
    await db.commit()
    return {
        "id": cursor.lastrowid,
        "req_code": req_code,
        "title": req.title,
        "description": req.description,
        "skills_needed": req.skills_needed,
        "team_size": req.team_size,
        "status": req.status,
    }


@router.get("/")
async def list_requirements(db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM requirements ORDER BY created_at DESC")
    rows = await cursor.fetchall()
    return [dict(row) for row in rows]


@router.get("/{req_id}")
async def get_requirement(req_id: int, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM requirements WHERE id = ?", (req_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Requirement not found")
    return dict(row)


@router.put("/{req_id}")
async def update_requirement(req_id: int, req: RequirementUpdate, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM requirements WHERE id = ?", (req_id,))
    existing = await cursor.fetchone()
    if not existing:
        raise HTTPException(status_code=404, detail="Requirement not found")

    existing_dict = dict(existing)
    updates = req.model_dump(exclude_unset=True)
    for key, value in updates.items():
        existing_dict[key] = value

    await db.execute(
        """UPDATE requirements SET title=?, description=?, skills_needed=?, team_size=?, status=?
           WHERE id=?""",
        (existing_dict["title"], existing_dict["description"], existing_dict["skills_needed"],
         existing_dict["team_size"], existing_dict["status"], req_id)
    )
    await db.commit()
    return existing_dict


@router.delete("/{req_id}")
async def delete_requirement(req_id: int, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM requirements WHERE id = ?", (req_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Requirement not found")
    await db.execute("DELETE FROM requirements WHERE id = ?", (req_id,))
    await db.commit()
    return {"message": "Requirement deleted"}


@router.get("/{req_id}/match-profiles")
async def match_profiles_for_requirement(
    req_id: int,
    db: aiosqlite.Connection = Depends(get_db),
):
    """Find matching profiles for a requirement using neural semantic search."""
    cursor = await db.execute("SELECT * FROM requirements WHERE id = ?", (req_id,))
    req_row = await cursor.fetchone()
    if not req_row:
        raise HTTPException(status_code=404, detail="Requirement not found")

    requirement = dict(req_row)
    skills_needed = requirement.get("skills_needed", "")
    title = requirement.get("title", "")
    description = requirement.get("description", "")

    # Build a search query from requirement details
    search_parts = []
    if skills_needed:
        search_parts.append(skills_needed)
    if title:
        search_parts.append(title)
    if description:
        search_parts.append(description)

    search_query = ". ".join(search_parts) if search_parts else title

    if not search_query.strip():
        return {"requirement": requirement, "matched_profiles": [], "search_query": ""}

    # Use FAISS semantic search
    results = semantic_search(search_query, n_results=10)

    SIMILARITY_THRESHOLD = 0.15
    filtered = [r for r in results if r["similarity"] >= SIMILARITY_THRESHOLD]

    # Enrich with full profile data from DB
    matched = []
    for result in filtered:
        pid = result["profile_id"]
        p_cursor = await db.execute(
            "SELECT id, name, email, phone, skills_json FROM profiles WHERE id = ?", (pid,)
        )
        p_row = await p_cursor.fetchone()
        if p_row:
            profile = dict(p_row)
            # Parse skills for display
            top_skills: list[str] = []
            if profile.get("skills_json"):
                try:
                    skills_data = json.loads(profile["skills_json"])
                    for cat in skills_data.get("skills", []):
                        if isinstance(cat, dict):
                            for s in cat.get("skills", []):
                                if isinstance(s, dict):
                                    top_skills.append(s.get("name", ""))
                except (json.JSONDecodeError, AttributeError):
                    pass

            matched.append({
                "profile_id": pid,
                "name": profile.get("name", "Unknown"),
                "email": profile.get("email", ""),
                "phone": profile.get("phone", ""),
                "similarity": result["similarity"],
                "top_skills": top_skills[:12],
            })

    return {
        "requirement": requirement,
        "matched_profiles": matched,
        "search_query": search_query,
    }

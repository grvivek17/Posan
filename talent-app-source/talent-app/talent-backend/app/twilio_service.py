"""Twilio integration for making real phone calls with TTS questions."""

import os
import logging
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse, Gather

logger = logging.getLogger(__name__)

def _get_sid() -> str:
    return os.getenv("TWILIO_ACCOUNT_SID", "")

def _get_token() -> str:
    return os.getenv("TWILIO_AUTH_TOKEN", "")

def _get_phone() -> str:
    return os.getenv("TWILIO_PHONE_NUMBER", "")


def get_twilio_client() -> Client | None:
    """Get Twilio client if credentials are configured."""
    sid, token = _get_sid(), _get_token()
    if not all([sid, token]):
        logger.warning("Twilio credentials not configured")
        return None
    return Client(sid, token)


def is_twilio_configured() -> bool:
    """Check if Twilio credentials are available."""
    return bool(_get_sid() and _get_token() and _get_phone())


def make_call(to_number: str, twiml_url: str) -> dict | None:
    """Initiate an outbound call via Twilio.
    
    Args:
        to_number: Phone number to call (E.164 format, e.g. +1234567890)
        twiml_url: URL that returns TwiML instructions for the call
        
    Returns:
        Dict with call_sid and status, or None if Twilio not configured
    """
    client = get_twilio_client()
    if not client:
        return None

    try:
        call = client.calls.create(
            to=to_number,
            from_=_get_phone(),
            url=twiml_url,
            status_callback=twiml_url.replace("/twiml/", "/status/"),
            status_callback_event=["initiated", "ringing", "answered", "completed"],
            status_callback_method="POST",
            record=True,
        )
        logger.info(f"Call initiated: SID={call.sid}, to={to_number}")
        return {"call_sid": call.sid, "status": call.status}
    except Exception as e:
        logger.error(f"Failed to make call: {e}")
        raise


def build_questions_twiml(
    questions: list[str],
    candidate_name: str,
    base_url: str,
    call_db_id: int,
) -> str:
    """Build TwiML that greets the candidate and asks the first question.
    
    The call flow is:
    1. Greet candidate
    2. Ask question 1, gather speech response
    3. Webhook receives response, asks question 2, etc.
    4. After last question, thank and hang up
    """
    response = VoiceResponse()

    if not questions:
        response.say(
            f"Hello {candidate_name}. Thank you for your time. We have no questions at this time. Goodbye.",
            voice="Polly.Joanna",
        )
        response.hangup()
        return str(response)

    response.say(
        f"Hello {candidate_name}. This is an automated screening call from the Talent Management team. "
        f"I will ask you {len(questions)} questions. Please speak your answer after each question. "
        f"Let's begin.",
        voice="Polly.Joanna",
    )
    response.pause(length=1)

    # Ask first question
    gather = Gather(
        input="speech",
        action=f"{base_url}/api/telecaller/twilio/gather/{call_db_id}/0",
        method="POST",
        speech_timeout="auto",
        language="en-US",
    )
    gather.say(f"Question 1: {questions[0]}", voice="Polly.Joanna")
    response.append(gather)

    # If no input, retry
    response.say("I didn't catch that. Let me repeat.", voice="Polly.Joanna")
    response.redirect(f"{base_url}/api/telecaller/twilio/twiml/{call_db_id}/0")

    return str(response)


def build_next_question_twiml(
    questions: list[str],
    question_index: int,
    base_url: str,
    call_db_id: int,
) -> str:
    """Build TwiML for the next question after receiving a response."""
    response = VoiceResponse()

    if question_index >= len(questions):
        # All questions asked
        response.say(
            "Thank you for answering all the questions. "
            "We appreciate your time and will get back to you soon. Goodbye.",
            voice="Polly.Joanna",
        )
        response.hangup()
        return str(response)

    response.say(
        f"Thank you. Next question.",
        voice="Polly.Joanna",
    )
    response.pause(length=1)

    gather = Gather(
        input="speech",
        action=f"{base_url}/api/telecaller/twilio/gather/{call_db_id}/{question_index}",
        method="POST",
        speech_timeout="auto",
        language="en-US",
    )
    gather.say(
        f"Question {question_index + 1}: {questions[question_index]}",
        voice="Polly.Joanna",
    )
    response.append(gather)

    # If no input, retry
    response.say("I didn't catch that. Let me repeat.", voice="Polly.Joanna")
    response.redirect(
        f"{base_url}/api/telecaller/twilio/twiml/{call_db_id}/{question_index}"
    )

    return str(response)


def get_call_status(call_sid: str) -> dict | None:
    """Fetch the current status of a Twilio call."""
    client = get_twilio_client()
    if not client:
        return None
    try:
        call = client.calls(call_sid).fetch()
        return {
            "status": call.status,
            "duration": call.duration,
            "start_time": str(call.start_time) if call.start_time else None,
            "end_time": str(call.end_time) if call.end_time else None,
        }
    except Exception as e:
        logger.error(f"Failed to fetch call status: {e}")
        return None

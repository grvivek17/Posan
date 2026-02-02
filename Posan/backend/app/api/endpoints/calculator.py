"""
Calculator API endpoints for Speaking Calculator feature
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.services.calculator_service import calculator_service
from app.services.tts_service import tts_service

router = APIRouter(prefix="/calculator", tags=["calculator"])


class TextCalculationRequest(BaseModel):
    """Request for text-based calculation"""
    text: str


class CalculationResponse(BaseModel):
    """Response for calculations"""
    success: bool
    error: Optional[str] = None
    transcription: str
    expression: str
    result: Optional[float] = None
    response_text: str
    audio_url: Optional[str] = None


@router.post("/voice", response_model=CalculationResponse)
async def calculate_from_voice(
    audio: UploadFile = File(..., description="Audio file (WAV, MP3, etc.)")
):
    """
    Voice-based calculation endpoint.
    
    Pipeline:
    1. Receive audio file
    2. ASR: Convert speech to text
    3. NLU: Parse math expression
    4. Evaluate safely
    5. Generate response text
    6. TTS: Create audio response
    
    Returns calculation result with audio URL.
    """
    try:
        print(f"[Calculator Voice] Received audio file: {audio.filename}, content_type: {audio.content_type}")
        
        # Read audio file
        audio_bytes = await audio.read()
        print(f"[Calculator Voice] Audio bytes read: {len(audio_bytes)} bytes")
        
        # Process voice calculation
        result = calculator_service.process_voice_calculation(audio_bytes)
        print(f"[Calculator Voice] Processing result: {result}")
        
        # Generate TTS audio response if successful
        audio_url = None
        if result['success'] and result['response_text']:
            try:
                # Generate TTS audio
                audio_filename = tts_service.generate_audio(
                    text=result['response_text'],
                    voice="en-US-JennyNeural",  # Kid-friendly voice
                    rate="-5%"  # Slightly slower for kids
                )
                
                if audio_filename:
                    # Return relative path for frontend
                    audio_url = f"/static/podcasts/{audio_filename}"
            except Exception as e:
                print(f"TTS generation failed: {e}")
                # Continue without audio - text response is still available
        
        return CalculationResponse(
            success=result['success'],
            error=result.get('error'),
            transcription=result['transcription'],
            expression=result['expression'],
            result=result['result'],
            response_text=result['response_text'],
            audio_url=audio_url
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/text", response_model=CalculationResponse)
async def calculate_from_text(request: TextCalculationRequest):
    """
    Text-based calculation endpoint.
    
    Accepts natural language math questions and returns the solution.
    
    Examples:
        - "What is twelve times seven?"
        - "Twenty five plus three"
        - "Five squared"
    """
    try:
        # Process text calculation
        result = calculator_service.process_text_calculation(request.text)
        
        # Generate TTS audio response if successful
        audio_url = None
        if result['success'] and result['response_text']:
            try:
                audio_filename = tts_service.generate_audio(
                    text=result['response_text'],
                    voice="en-US-JennyNeural",
                    rate="-5%"
                )
                
                if audio_filename:
                    audio_url = f"/static/podcasts/{audio_filename}"
            except Exception as e:
                print(f"TTS generation failed: {e}")
        
        return CalculationResponse(
            success=result['success'],
            error=result.get('error'),
            transcription=result['transcription'],
            expression=result['expression'],
            result=result['result'],
            response_text=result['response_text'],
            audio_url=audio_url
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/test")
async def test_calculator():
    """Test endpoint to verify calculator is working"""
    test_cases = [
        "What is twelve times seven?",
        "Twenty five plus three",
        "Five squared",
        "One hundred divided by four"
    ]
    
    results = []
    for test in test_cases:
        result = calculator_service.process_text_calculation(test)
        results.append({
            'input': test,
            'expression': result['expression'],
            'result': result['result'],
            'success': result['success']
        })
    
    return {
        'message': 'Calculator test completed',
        'test_cases': results
    }

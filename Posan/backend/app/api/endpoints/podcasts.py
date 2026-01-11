"""
Podcast API Endpoints
"""
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
import os
from app.services.podcast_service import podcast_generator
from app.services.tts_service import tts_service

router = APIRouter()


class PodcastRequest(BaseModel):
    """Request model for podcast generation"""
    topic: str
    age_group: Optional[str] = "8-12"
    duration: Optional[str] = "short"  # short, medium, long
    style: Optional[str] = "fun"  # fun, educational, story


class WeeklyHighlightsRequest(BaseModel):
    """Request model for weekly highlights"""
    topics: Optional[List[str]] = None


@router.post("/generate")
async def generate_podcast(request: PodcastRequest):
    """
    Generate a personalized podcast on any topic
    
    **Example requests:**
    - "Tell me a fun fact about dinosaurs"
    - "Explain how volcanoes work"
    - "Tell me a story about space exploration"
    
    **Parameters:**
    - topic: What the podcast should be about
    - age_group: Target age (6-8, 8-12, 12-14)
    - duration: short (2-3 min), medium (5 min), long (10 min)
    - style: fun, educational, or story
    """
    
    try:
        result = podcast_generator.generate_podcast_script(
            topic=request.topic,
            age_group=request.age_group,
            duration=request.duration,
            style=request.style
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to generate podcast")
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/weekly-highlights")
async def generate_weekly_highlights(request: WeeklyHighlightsRequest):
    """
    Generate a weekly highlights podcast
    
    Summarizes the week's most interesting topics from magazines
    """
    
    try:
        result = podcast_generator.generate_weekly_highlights(
            magazine_topics=request.topics or []
        )
        
        if not result.get("success"):
            raise HTTPException(
                status_code=500,
                detail=result.get("error", "Failed to generate weekly highlights")
            )
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/suggestions")
async def get_topic_suggestions():
    """
    Get suggested podcast topics for kids
    """
    
    suggestions = {
        "popular": [
            "Dinosaurs and prehistoric life",
            "Space and planets",
            "Ocean animals and sea creatures",
            "How airplanes fly",
            "Ancient Egypt and pyramids",
            "Volcanoes and earthquakes",
            "The human body",
            "Robots and AI",
            "Weather and storms",
            "Rainforests and jungles"
        ],
        "science": [
            "How plants grow",
            "The water cycle",
            "Electricity and circuits",
            "Magnets and magnetism",
            "Sound and music",
            "Light and colors",
            "Chemical reactions",
            "Gravity and forces"
        ],
        "history": [
            "Ancient civilizations",
            "Famous inventors",
            "Medieval castles and knights",
            "Pirates and explorers",
            "The first humans",
            "Ancient Rome",
            "Vikings and their ships"
        ],
        "nature": [
            "Endangered animals",
            "How bees make honey",
            "Migration of birds",
            "Life in the desert",
            "Arctic and Antarctic",
            "Coral reefs",
            "Forests and trees"
        ],
        "technology": [
            "How computers work",
            "The internet explained",
            "3D printing",
            "Renewable energy",
            "Smartphones and apps",
            "Virtual reality",
            "Coding and programming"
        ]
    }
    
    return {
        "suggestions": suggestions,
        "total_topics": sum(len(topics) for topics in suggestions.values())
    }


@router.get("/examples")
async def get_example_podcasts():
    """
    Get example podcast requests to inspire kids
    """
    
    examples = [
        {
            "request": "Tell me a fun fact about dinosaurs",
            "style": "fun",
            "duration": "short",
            "description": "Quick and exciting dinosaur facts!"
        },
        {
            "request": "How do rockets work?",
            "style": "educational",
            "duration": "medium",
            "description": "Learn about rocket science in simple terms"
        },
        {
            "request": "A story about exploring the ocean",
            "style": "story",
            "duration": "medium",
            "description": "An underwater adventure story"
        },
        {
            "request": "Why is the sky blue?",
            "style": "educational",
            "duration": "short",
            "description": "Science made simple and fun"
        },
        {
            "request": "Tell me about ancient Egypt",
            "style": "fun",
            "duration": "medium",
            "description": "Discover pharaohs, pyramids, and mummies!"
        }
    ]
    
    return {"examples": examples}


# ============= AUDIO GENERATION ENDPOINTS =============

@router.post("/generate-audio")
async def generate_podcast_audio(
    text: str,
    voice: Optional[str] = "en-US-AriaNeural",
    podcast_id: Optional[str] = None
):
    """
    Generate audio file from podcast script
    
    **Parameters:**
    - text: The podcast script text
    - voice: Voice to use (default: Aria - friendly female voice)
    - podcast_id: Optional ID for caching
    
    **Returns:**
    - Audio file URL and metadata
    """
    
    try:
        result = tts_service.generate_audio(
            text=text,
            voice=voice,
            podcast_id=podcast_id
        )
        
        if not result.get("success"):
            # Return fallback info for browser TTS
            return {
                "success": False,
                "error": result.get("error"),
                "fallback": "browser_tts",
                "message": "Audio generation not available. Use browser's built-in speech."
            }
        
        return result
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "fallback": "browser_tts"
        }


@router.get("/audio/{filename}")
async def get_audio_file(filename: str):
    """
    Serve generated audio file
    """
    filepath = os.path.join("static/podcasts", filename)
    
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="Audio file not found")
    
    return FileResponse(
        filepath,
        media_type="audio/mpeg",
        filename=filename
    )


@router.get("/voices")
async def get_available_voices():
    """
    Get list of available kid-friendly voices for TTS
    """
    try:
        voices = await tts_service.get_available_voices()
        return {"voices": voices}
    except Exception as e:
        # Return default voices
        return {
            "voices": [
                {"name": "en-US-AriaNeural", "gender": "Female", "locale": "en-US", "friendly_name": "Aria (Friendly)"},
                {"name": "en-US-GuyNeural", "gender": "Male", "locale": "en-US", "friendly_name": "Guy (Energetic)"},
                {"name": "en-US-JennyNeural", "gender": "Female", "locale": "en-US", "friendly_name": "Jenny (Warm)"},
            ]
        }

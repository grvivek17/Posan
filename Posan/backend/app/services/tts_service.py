"""
Text-to-Speech Service for Podcast Audio Generation
Uses edge-tts (Microsoft Edge TTS) for high-quality, free text-to-speech
"""
import os
import asyncio
from typing import Optional
import hashlib


class TTSService:
    """Generate audio from podcast scripts using Text-to-Speech"""
    
    def __init__(self):
        self.audio_dir = "static/podcasts"
        self.ensure_audio_directory()
    
    def ensure_audio_directory(self):
        """Create audio directory if it doesn't exist"""
        os.makedirs(self.audio_dir, exist_ok=True)
    
    async def generate_audio_async(
        self,
        text: str,
        voice: str = "en-US-AriaNeural",  # Kid-friendly voice
        rate: str = "+0%",  # Speech rate
        podcast_id: Optional[str] = None
    ) -> dict:
        """
        Generate audio file from text using edge-tts
        
        Args:
            text: The podcast script text
            voice: Voice to use (default: Aria - friendly female voice)
            rate: Speech rate adjustment
            podcast_id: Optional ID for caching
        
        Returns:
            Dictionary with audio file path and metadata
        """
        try:
            import edge_tts
            
            # Generate filename based on content hash or ID
            if podcast_id:
                filename = f"podcast_{podcast_id}.mp3"
            else:
                text_hash = hashlib.md5(text.encode()).hexdigest()[:12]
                filename = f"podcast_{text_hash}.mp3"
            
            filepath = os.path.join(self.audio_dir, filename)
            
            # Check if already generated
            if os.path.exists(filepath):
                return {
                    "success": True,
                    "audio_path": filepath,
                    "audio_url": f"/static/podcasts/{filename}",
                    "cached": True
                }
            
            # Clean text for TTS (remove section markers)
            clean_text = self._clean_text_for_tts(text)
            
            # Generate audio
            communicate = edge_tts.Communicate(clean_text, voice, rate=rate)
            await communicate.save(filepath)
            
            return {
                "success": True,
                "audio_path": filepath,
                "audio_url": f"/static/podcasts/{filename}",
                "cached": False,
                "voice": voice
            }
            
        except ImportError:
            return {
                "success": False,
                "error": "edge-tts not installed. Run: pip install edge-tts",
                "fallback": "browser_tts"  # Use browser's built-in TTS
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "fallback": "browser_tts"
            }
    
    def generate_audio(self, text: str, **kwargs) -> dict:
        """Synchronous wrapper for generate_audio_async"""
        return asyncio.run(self.generate_audio_async(text, **kwargs))
    
    def _clean_text_for_tts(self, text: str) -> str:
        """Clean text for better TTS output"""
        # Remove section markers like [INTRO], [MAIN CONTENT], etc.
        import re
        text = re.sub(r'\[.*?\]', '', text)
        
        # Remove sound effect markers like *whoosh*, *ding*
        text = re.sub(r'\*.*?\*', '', text)
        
        # Remove emojis (they don't sound good in TTS)
        text = re.sub(r'[🎙️📚🌟✨🎉📖🔬🌍🎨🎯🚀💡🏆⭐🎧📅]', '', text)
        
        # Clean up extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    
    async def get_available_voices(self) -> list:
        """Get list of available kid-friendly voices"""
        try:
            import edge_tts
            
            voices = await edge_tts.list_voices()
            
            # Filter for English voices suitable for kids
            kid_friendly = []
            
            for v in voices:
                if not v['Locale'].startswith('en-'):
                    continue
                
                name = v['ShortName']
                friendly = v.get('FriendlyName', '')
                
                # Prioritize kid/teen voices
                is_kid_voice = any(keyword in name.lower() or keyword in friendly.lower() for keyword in [
                    'child', 'kid', 'teen', 'young', 'girl', 'boy'
                ])
                
                # Also include friendly adult voices
                is_friendly_voice = any(keyword in name for keyword in [
                    'Aria', 'Jenny', 'Guy', 'Davis', 'Amber', 'Ana', 
                    'Ashley', 'Brandon', 'Christopher', 'Emma', 'Michelle',
                    'Sara', 'Tony', 'Nancy'
                ])
                
                if is_kid_voice or is_friendly_voice:
                    kid_friendly.append({
                        "name": v['ShortName'],
                        "gender": v['Gender'],
                        "locale": v['Locale'],
                        "friendly_name": v.get('FriendlyName', v['ShortName']),
                        "is_kid_voice": is_kid_voice
                    })
            
            # Sort: kid voices first, then by gender
            kid_friendly.sort(key=lambda x: (not x['is_kid_voice'], x['gender']))
            
            return kid_friendly[:15]  # Top 15
            
        except:
            # Default fallback voices with kid-appropriate options
            return [
                # Kid/Teen voices (if available)
                {"name": "en-US-GuyNeural", "gender": "Male", "locale": "en-US", "friendly_name": "Guy (Energetic Teen)", "is_kid_voice": True},
                {"name": "en-US-JennyNeural", "gender": "Female", "locale": "en-US", "friendly_name": "Jenny (Young & Warm)", "is_kid_voice": True},
                
                # Friendly adult voices
                {"name": "en-US-AriaNeural", "gender": "Female", "locale": "en-US", "friendly_name": "Aria (Friendly)", "is_kid_voice": False},
                {"name": "en-US-DavisNeural", "gender": "Male", "locale": "en-US", "friendly_name": "Davis (Clear)", "is_kid_voice": False},
                {"name": "en-US-AmberNeural", "gender": "Female", "locale": "en-US", "friendly_name": "Amber (Cheerful)", "is_kid_voice": False},
                {"name": "en-US-AshleyNeural", "gender": "Female", "locale": "en-US", "friendly_name": "Ashley (Sweet)", "is_kid_voice": False},
                {"name": "en-US-BrandonNeural", "gender": "Male", "locale": "en-US", "friendly_name": "Brandon (Friendly)", "is_kid_voice": False},
                {"name": "en-US-ChristopherNeural", "gender": "Male", "locale": "en-US", "friendly_name": "Christopher (Calm)", "is_kid_voice": False},
                {"name": "en-US-EmmaNeural", "gender": "Female", "locale": "en-US", "friendly_name": "Emma (Bright)", "is_kid_voice": False},
                {"name": "en-US-MichelleNeural", "gender": "Female", "locale": "en-US", "friendly_name": "Michelle (Gentle)", "is_kid_voice": False},
            ]
    
    def delete_old_audio_files(self, max_files: int = 50):
        """Clean up old audio files to save space"""
        try:
            files = [
                os.path.join(self.audio_dir, f)
                for f in os.listdir(self.audio_dir)
                if f.endswith('.mp3')
            ]
            
            if len(files) > max_files:
                # Sort by modification time
                files.sort(key=os.path.getmtime)
                
                # Delete oldest files
                for f in files[:len(files) - max_files]:
                    os.remove(f)
                    
                return {"deleted": len(files) - max_files}
            
            return {"deleted": 0}
            
        except Exception as e:
            return {"error": str(e)}


# Global instance
tts_service = TTSService()

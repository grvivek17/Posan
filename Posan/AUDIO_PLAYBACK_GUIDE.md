# 🎧 How to Play Audio in the Podcast App

## Overview

The podcast app now has **TWO ways** to play audio:

1. **Browser's Built-in Text-to-Speech** (Always works, no setup needed)
2. **Server-Side TTS with edge-tts** (Better quality, requires installation)

---

## 🚀 Quick Start - Browser TTS (No Setup Required)

The app automatically uses your browser's built-in speech synthesis! Just:

1. **Generate a podcast**
2. **Click the "▶️ Play" button**
3. **Listen!**

✅ **Works immediately** - No installation needed  
✅ **Works on all modern browsers**  
✅ **Kid-friendly voices** automatically selected  

---

## 🎵 Advanced Setup - High-Quality Server TTS (Optional)

For better quality audio with downloadable MP3 files:

### Step 1: Install edge-tts

```bash
cd backend
pip install edge-tts
```

### Step 2: Restart Backend

The backend will automatically detect edge-tts and use it!

```bash
# Backend will reload automatically if using --reload
# Or restart manually:
uvicorn app.main:app --reload
```

### Step 3: Test It!

Generate a podcast and click Play - you'll now get high-quality MP3 audio!

---

## 🎙️ How the Audio Player Works

### Features:

✅ **Play/Pause/Stop Controls**  
✅ **Automatic voice selection** (kid-friendly)  
✅ **Clean text processing** (removes emojis, markers)  
✅ **Audio caching** (faster subsequent plays)  
✅ **Fallback support** (always works)  
✅ **Visual feedback** (loading states, errors)  

### Audio Player UI:

```
┌─────────────────────────────────────┐
│  🎧 Listen to Podcast               │
│  Your Podcast Topic                 │
├─────────────────────────────────────┤
│  [▶️ Play]  [⏸️ Pause]  [⏹️ Stop]   │
│                                     │
│  🔊 Using browser's built-in voice  │
└─────────────────────────────────────┘
```

---

## 🔊 Available Voices

### Browser TTS Voices:
- Automatically selects kid-friendly voices
- Varies by browser and OS
- Common voices: Google Female, Samantha, etc.

### Server TTS Voices (with edge-tts):
- **Aria** (Friendly Female) - Default
- **Guy** (Energetic Male)
- **Jenny** (Warm Female)
- **Davis** (Clear Male)
- And many more!

---

## 📖 Usage Guide

### 1. Generate a Podcast

```
1. Go to Magazines → AI Podcasts
2. Enter topic: "Tell me about dinosaurs"
3. Select preferences
4. Click "Generate Podcast"
```

### 2. Play the Audio

```
1. Podcast opens in player
2. Click "▶️ Play" button
3. Listen to the podcast!
```

### 3. Player Controls

- **▶️ Play** - Start playing
- **⏸️ Pause** - Pause playback
- **▶️ Resume** - Continue from pause
- **⏹️ Stop** - Stop and reset

---

## 🛠️ Technical Details

### Browser TTS (Default):

**Technology:** Web Speech API  
**Format:** Real-time synthesis  
**Quality:** Good  
**Latency:** Instant  
**Storage:** None (generated on-the-fly)  

**Pros:**
- ✅ No setup required
- ✅ Works everywhere
- ✅ Instant playback
- ✅ No server load

**Cons:**
- ⚠️ Voice quality varies by browser
- ⚠️ Can't download audio
- ⚠️ Limited voice options

### Server TTS (with edge-tts):

**Technology:** Microsoft Edge TTS  
**Format:** MP3 audio files  
**Quality:** Excellent  
**Latency:** 2-5 seconds (first time)  
**Storage:** Cached on server  

**Pros:**
- ✅ High-quality voices
- ✅ Consistent across devices
- ✅ Downloadable MP3 files
- ✅ Multiple voice options
- ✅ Cached for speed

**Cons:**
- ⚠️ Requires pip install
- ⚠️ Uses server storage
- ⚠️ Slight delay on first play

---

## 🎯 API Endpoints

### Generate Audio

```http
POST /api/v1/podcasts/generate-audio
Content-Type: application/x-www-form-urlencoded

text=Your podcast script here
voice=en-US-AriaNeural
podcast_id=12345
```

**Response:**
```json
{
  "success": true,
  "audio_url": "/static/podcasts/podcast_12345.mp3",
  "audio_path": "static/podcasts/podcast_12345.mp3",
  "cached": false,
  "voice": "en-US-AriaNeural"
}
```

### Get Audio File

```http
GET /api/v1/podcasts/audio/{filename}
```

Returns MP3 audio file.

### Get Available Voices

```http
GET /api/v1/podcasts/voices
```

**Response:**
```json
{
  "voices": [
    {
      "name": "en-US-AriaNeural",
      "gender": "Female",
      "locale": "en-US",
      "friendly_name": "Aria (Friendly)"
    },
    ...
  ]
}
```

---

## 🔧 Troubleshooting

### Issue: "Failed to play audio"

**Solution:**
- Browser TTS always works as fallback
- Check browser console for errors
- Try a different browser

### Issue: "Audio generation not available"

**Solution:**
```bash
# Install edge-tts
pip install edge-tts

# Restart backend
# It will auto-detect and use edge-tts
```

### Issue: "No sound playing"

**Solution:**
- Check device volume
- Check browser permissions
- Try clicking Play again
- Refresh the page

### Issue: "Audio file not found"

**Solution:**
- Audio files are cached in `static/podcasts/`
- They auto-delete after 50 files
- Generate audio again if needed

---

## 📊 Audio File Management

### Caching:
- Audio files are cached in `static/podcasts/`
- Filename format: `podcast_{id}.mp3`
- Cached files are reused for same content

### Cleanup:
- Automatically deletes old files
- Keeps last 50 audio files
- Prevents storage bloat

### Storage Location:
```
backend/
  static/
    podcasts/
      podcast_12345.mp3
      podcast_67890.mp3
      ...
```

---

## 🎨 Customization

### Change Default Voice:

In `AudioPlayer.jsx`:
```javascript
// Line ~30
const preferredVoice = voices.find(v => 
    v.name.includes('YOUR_PREFERRED_VOICE')
);
```

### Adjust Speech Rate:

In `AudioPlayer.jsx`:
```javascript
// Line ~26
utterance.rate = 0.9;  // 0.5 = slow, 1.0 = normal, 2.0 = fast
```

### Adjust Pitch:

In `AudioPlayer.jsx`:
```javascript
// Line ~27
utterance.pitch = 1.1;  // 0.5 = low, 1.0 = normal, 2.0 = high
```

---

## 📱 Mobile Support

### iOS:
✅ Browser TTS works  
✅ Server TTS works  
✅ Audio controls work  

### Android:
✅ Browser TTS works  
✅ Server TTS works  
✅ Audio controls work  

### Tablets:
✅ Full support  
✅ Responsive UI  

---

## 🚀 Performance Tips

### For Best Performance:

1. **Use Server TTS** (install edge-tts)
   - Better quality
   - Cached files
   - Faster subsequent plays

2. **Keep Cache Warm**
   - Popular podcasts stay cached
   - Instant playback for cached content

3. **Optimize Script Length**
   - Shorter scripts = faster generation
   - Use "short" duration for quick content

---

## 🎓 Example Usage

### Example 1: Quick Fact

```javascript
// Generate short podcast
Topic: "Fun fact about dinosaurs"
Duration: Short
Style: Fun

// Result: 2-3 minute audio
// Playback: Instant with browser TTS
```

### Example 2: Educational Content

```javascript
// Generate educational podcast
Topic: "How do volcanoes work?"
Duration: Medium
Style: Educational

// Result: 5 minute audio
// Playback: High-quality with server TTS
```

### Example 3: Story Time

```javascript
// Generate story podcast
Topic: "Adventure in space"
Duration: Long
Style: Story

// Result: 10 minute audio story
// Playback: Engaging narration
```

---

## 📚 Additional Resources

### Web Speech API:
- [MDN Documentation](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)

### edge-tts:
- [GitHub Repository](https://github.com/rany2/edge-tts)
- [PyPI Package](https://pypi.org/project/edge-tts/)

### Audio Formats:
- MP3: Universal support
- Bitrate: 128kbps (good quality)
- Sample Rate: 24kHz (clear speech)

---

## ✅ Summary

**Two Ways to Play Audio:**

1. **Browser TTS** (Default)
   - No setup
   - Works everywhere
   - Instant playback

2. **Server TTS** (Optional)
   - Install: `pip install edge-tts`
   - Better quality
   - Downloadable files

**Both methods work seamlessly with automatic fallback!**

---

## 🎉 You're Ready!

The audio player is fully integrated and ready to use!

Just generate a podcast and click **▶️ Play** to listen! 🎧✨

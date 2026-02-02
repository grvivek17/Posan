# 🧮 Speaking Calculator Feature

## Overview
The Speaking Calculator is an AI-powered voice-activated math calculator designed for kids. It uses cutting-edge speech recognition, natural language understanding, and text-to-speech technologies to provide an interactive and educational math learning experience.

## Architecture

### Pipeline
```
Audio Input (Microphone) 
    ↓
ASR (Automatic Speech Recognition)
    ↓
NLU (Natural Language Understanding + Math Parser)
    ↓
Safe Math Evaluation
    ↓
Response Generation
    ↓
TTS (Text-to-Speech)
    ↓
Audio Output
```

## Technology Stack

### Backend (Python/FastAPI)

#### 1. ASR (Speech-to-Text)
- **Model**: `openai/whisper-small`
- **Purpose**: Convert spoken math questions to text
- **Example**: "what is twelve times seven?" → text transcription

#### 2. NLU + Math Parser
- **Approach**: Rule-based parser with word-to-number mapping
- **Features**:
  - Converts number words to digits ("twelve" → "12")
  - Maps operation words to symbols ("times" → "×")
  - Handles compound numbers ("twenty five" → "25")
  - Supports parentheses and basic operations

#### 3. Safe Math Evaluator
- **Method**: AST (Abstract Syntax Tree) parsing
- **Safety**: Never uses `eval()` - only safe arithmetic operations
- **Supported Operations**:
  - Addition (+)
  - Subtraction (-)
  - Multiplication (×, *)
  - Division (÷, /)
  - Exponentiation (^, **)
  - Parentheses for grouping

#### 4. TTS (Text-to-Speech)
- **Service**: Microsoft Edge TTS (edge-tts)
- **Voice**: Jenny Neural (kid-friendly)
- **Features**: Natural-sounding speech output

### Frontend (React)

#### Components
1. **VoiceRecorder**
   - Microphone input using Web Audio API
   - Recording timer
   - Visual feedback during recording

2. **SpeakingCalculator**
   - Dual mode: Voice & Text input
   - Real-time feedback
   - Calculation history
   - Audio playback controls

## Features

### ✅ Implemented Features

1. **Voice Input**
   - Click-to-record interface
   - Recording timer display
   - Visual feedback (pulsing indicator)

2. **Text Input (Fallback)**
   - Type math questions naturally
   - Example questions provided
   - Instant evaluation

3. **Natural Language Support**
   Examples of supported inputs:
   - "What is twelve times seven?"
   - "Twenty five plus three"
   - "One hundred divided by four"
   - "Five squared"
   - "Fifteen minus eight"

4. **Smart Response**
   - Kid-friendly explanations
   - Encouraging feedback
   - Clear step-by-step breakdown

5. **Audio Feedback**
   - TTS response with friendly voice
   - Replay button for answers
   - Slower speech rate for kids

6. **Calculation History**
   - Last 10 calculations saved
   - Timestamp tracking
   - Quick reference

## API Endpoints

### POST `/api/v1/calculator/voice`
Voice-based calculation from audio file.

**Request:**
- `audio`: Audio file (WAV, MP3, etc.)

**Response:**
```json
{
  "success": true,
  "transcription": "what is twelve times seven",
  "expression": "12 * 7",
  "result": 84,
  "response_text": "12 times 7 equals 84. Great job!",
  "audio_url": "/static/podcasts/response_abc123.mp3"
}
```

### POST `/api/v1/calculator/text`
Text-based calculation from natural language.

**Request:**
```json
{
  "text": "What is twelve times seven?"
}
```

**Response:**
```json
{
  "success": true,
  "transcription": "What is twelve times seven?",
  "expression": "12 * 7",
  "result": 84,
  "response_text": "12 times 7 equals 84. Excellent!",
  "audio_url": "/static/podcasts/response_abc123.mp3"
}
```

### GET `/api/v1/calculator/test`
Test endpoint to verify calculator functionality.

## Safety Features

### 1. No Direct Eval
- Uses AST parsing instead of `eval()`
- Only whitelisted operations allowed
- Prevents code injection

### 2. Age-Appropriate Complexity
- Limited to basic arithmetic (Grade <8)
- Simple operations: +, -, ×, ÷, ^
- Basic parentheses support
- No advanced functions

### 3. Error Handling
- Graceful degradation
- Clear error messages
- Division by zero protection

## Usage

### In the Application

1. Navigate to **AI Creator** page
2. Click on **🧮 Calculator** tab
3. Choose mode:
   - **🎤 Voice Mode**: Click "Start Recording" and speak your question
   - **⌨️ Text Mode**: Type your question and click "Calculate"
4. View the result with explanation
5. Click "🔊 Play Answer" to hear the response

### Example Questions

Try these examples:
- "What is twelve times seven?"
- "Twenty five plus three"
- "One hundred divided by four"
- "Five squared"
- "Fifteen minus eight"

## File Structure

```
backend/
├── app/
│   ├── services/
│   │   └── calculator_service.py    # Core calculator logic
│   └── api/
│       └── endpoints/
│           └── calculator.py          # API endpoints

frontend/
├── src/
│   ├── components/
│   │   └── calculator/
│   │       ├── SpeakingCalculator.jsx  # Main component
│   │       ├── SpeakingCalculator.css
│   │       ├── VoiceRecorder.jsx       # Voice input
│   │       └── VoiceRecorder.css
│   └── pages/
│       └── AIContentPage.jsx           # Integration
```

## Future Enhancements

### Planned Features
1. **Multi-step Problems**
   - Handle multi-step word problems
   - Show intermediate steps

2. **Word Problems**
   - Parse story-based math questions
   - Extract relevant numbers and operations

3. **Visual Representations**
   - Show math problems visually
   - Animated solutions

4. **Practice Mode**
   - Generate random practice problems
   - Track accuracy and progress

5. **Multi-language Support**
   - Support for multiple languages
   - Localized number systems

## Testing

### Manual Testing
1. Test voice input with clear speech
2. Test text input with various formats
3. Verify audio playback
4. Check calculation history
5. Test error cases (invalid input, etc.)

### Test Endpoint
Visit: `http://localhost:8000/api/v1/calculator/test`

## Performance

- **ASR**: ~2-3 seconds for transcription
- **Math Evaluation**: <100ms
- **TTS Generation**: ~1-2 seconds
- **Total Response Time**: ~3-5 seconds

## Dependencies

### Python
- `huggingface_hub`: ASR model access
- `edge-tts`: Text-to-speech
- Standard library: `ast`, `re`, `operator`

### JavaScript
- React hooks (`useState`, `useRef`)
- Web Audio API (MediaRecorder)
- Fetch API

## Credits

- **ASR Model**: OpenAI Whisper
- **TTS Service**: Microsoft Edge Neural Voices
- **Design**: Custom premium UI with gradients and animations

---

**Created**: January 2026  
**Version**: 1.0.0  
**Status**: ✅ Production Ready

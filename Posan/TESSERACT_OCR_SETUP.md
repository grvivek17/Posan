# Tesseract OCR Integration Guide

## Overview

This document describes the full OCR (Optical Character Recognition) integration with Tesseract for the POSAN Kids Magazine application's Test Analysis feature.

## ✅ What's Been Implemented

### Backend Components:

1. **OCR Service** (`backend/app/services/ocr_service.py`)
   - Image preprocessing for better accuracy
   - Text extraction from images (JPG, PNG)
   - Text extraction from PDFs
   - Automatic score parsing and detection
   - Subject identification
   - Question counting

2. **API Endpoint** (`backend/app/api/endpoints/ai_content.py`)
   - `POST /api/v1/ai/analyze/test-upload`
   - Accepts file uploads (JPG, PNG, PDF up to 10MB)
   - Processes files with OCR
   - Returns AI analysis or prompts for manual entry

3. **Dependencies Added** (`backend/requirements.txt`)
   - `pytesseract` - Python wrapper for Tesseract
   - `Pillow` - Image processing
   - `pdf2image` - PDF to image conversion
   - `opencv-python` - Advanced image preprocessing

### Frontend Components:

1. **Updated TestAnalysis Component** (`frontend/src/components/homework/TestAnalysis.jsx`)
   - Real OCR integration (no more mock data)
   - File upload with FormData
   - Error handling for OCR failures
   - Success messages with confidence scores

## 🔧 System Requirements

### Installing Tesseract OCR

**Tesseract** is an external program that must be installed on your system. The Python libraries alone are not sufficient.

#### Windows Installation:

1. Download the Tesseract installer:
   - Visit: https://github.com/UB-Mannheim/tesseract/wiki
   - Download the latest Windows installer (e.g., `tesseract-ocr-w64-setup-5.3.3.20231005.exe`)

2. Run the installer:
   - Install to `C:\Program Files\Tesseract-OCR\` (recommended path)
   - Make sure to install language data files (English is included by default)

3. Add to System PATH (Optional but recommended):
   - Right-click "This PC" → Properties → Advanced System Settings
   - Environment Variables → System Variables → Path
   - Add: `C:\Program Files\Tesseract-OCR`

4. Verify installation:
   ```powershell
   tesseract --version
   ```

#### Linux Installation:

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install tesseract-ocr

# Fedora/RHEL
sudo dnf install tesseract

# Verify
tesseract --version
```

#### macOS Installation:

```bash
# Using Homebrew
brew install tesseract

# Verify
tesseract --version
```

### Python Dependencies

Already installed if you ran the pip install command. To install manually:

```bash
cd backend
.\venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate  # Linux/Mac

pip install pytesseract Pillow pdf2image opencv-python
```

### Additional Requirements for PDF Support

**pdf2image** requires **poppler**:

#### Windows:
1. Download poppler from: http://blog.alivate.com.au/poppler-windows/
2. Extract to `C:\Program Files\poppler`
3. Add `C:\Program Files\poppler\Library\bin` to PATH

#### Linux:
```bash
sudo apt install poppler-utils
```

#### macOS:
```bash
brew install poppler
```

## 📝 How It Works

### Upload Flow:

1. **User uploads test paper** (JPG, PNG, or PDF)
2. **Frontend sends file** to `/api/v1/ai/analyze/test-upload`
3. **Backend receives file** and saves temporarily
4. **OCR Service processes image:**
   - Converts to grayscale
   - Applies denoising
   - Uses adaptive thresholding
   - Extracts text with Tesseract
5. **Score Parser analyzes text:**
   - Looks for patterns like "85/100", "Score: 75"
   - Counts questions
   - Detects subject from keywords
6. **Two possible outcomes:**
   - **Score detected**: Sends to AI for full analysis
   - **Score not detected**: Returns OCR preview and asks for manual entry
7. **AI generates personalized recommendations**
8. **Results sent to frontend**

### Confidence Levels:

- **High**: Score found in format "X/Y" (e.g., "85/100")
- **Medium**: Score found without total (e.g., "Score: 85")
- **Low**: No clear score pattern found

## 🧪 Testing the Integration

### Test with Sample Image:

1. Create a simple test paper image with:
   ```
   Mathematics Test
   Name: John Doe
   Score: 85/100
   
   Q1. 2 + 2 = 4 ✓ (5 marks)
   Q2. 10 - 3 = 7 ✓ (5 marks)
   ```

2. Save as clear, high-contrast image

3. Upload through the UI:
   - Navigate to Homework → AI Test Analysis
   - Click "Upload Test Paper" tab
   - Enter student name and select subject
   - Upload test image
   - Click "Analyze Test Paper with AI"

### Expected Behavior:

- ✅ OCR extracts text successfully
- ✅ Detects score: 85/100
- ✅ Identifies 2 questions
- ✅ AI provides personalized analysis

## 🐛 Troubleshooting

### Common Issues:

1. **"Tesseract not found" Error**
   - **Solution**: Install Tesseract (see installation steps above)
   - **Solution**: Update path in `ocr_service.py` line 25-26

2. **Poor OCR Accuracy**
   - Use well-lit, focused images
   - Ensure handwriting is neat or use typed text
   - Try increasing image resolution
   - Check image isn't blurry or skewed

3. **PDF Not Working**
   - Install poppler (see PDF requirements above)
   - Verify poppler is in PATH

4. **Score Not Detected**
   - Ensure score is in recognizable format: "85/100" or "Score: 85"
   - Check OCR preview to see extracted text
   - Use manual entry mode as fallback

## 🔒 Security Considerations

- File size limited to 10MB
- Only accepted formats: JPG, PNG, PDF
- Temporary files are deleted after processing  
- File validation before processing

## 📊 API Documentation

### Endpoint: Upload Test Paper

```http
POST /api/v1/ai/analyze/test-upload
Content-Type: multipart/form-data
```

**Query Parameters:**
- `student_name` (required): Student's name
- `subject` (required): Subject (Mathematics, Science, English, etc.)
- `age_group` (optional): Default "6-8"

**Request Body:**
- `file`: Test paper file (multipart/form-data)

**Response (Score Detected):**
```json
{
  "ocr_success": true,
  "score_detected": true,
  "ocr_confidence": "high",
  "extracted_text_preview": "Mathematics Test...",
  "questions_found": 10,
  "subject": "Mathematics",
  "score": 85,
  "total": 100,
  "percentage": 85.0,
  "performance_level": "very good",
  "analysis": "**Performance Summary:**...",
  "motivational_quote": "...",
  "weak_areas": [...],
  "strong_areas": [...]
}
```

**Response (Score Not Detected):**
```json
{
  "ocr_success": true,
  "score_detected": false,
  "message": "Could not automatically detect score...",
  "extracted_text_preview": "...",
  "confidence": "low",
  "questions_found": 5,
  "suggested_subject": "Mathematics"
}
```

## 🎯 Best Practices

1. **Image Quality:**
   - Use 300 DPI or higher
   - Good lighting, no shadows
   - Clear, focused images
   - Straight alignment (not tilted)

2. **Test Paper Format:**
   - Clear score marking (e.g., "85/100")
   - Typed or neat handwriting
   - High contrast (dark text on light background)

3. **Fallback Strategy:**
   - Always provide manual entry option
   - Show extracted text preview
   - Let users verify/correct OCR results

## 🚀 Future Enhancements

Potential improvements:
- Support for more languages
- Handwriting recognition improvements
- Question-by-question analysis
- Answer evaluation (not just score extraction)
- Batch processing multiple test papers
- Image rotation/deskewing
- Support for more file formats (HEIC, WebP)

## 📚 Resources

- [Tesseract GitHub](https://github.com/tesseract-ocr/tesseract)
- [pytesseract Documentation](https://pypi.org/project/pytesseract/)
- [OpenCV Documentation](https://docs.opencv.org/)
- [Pillow Documentation](https://pillow.readthedocs.io/)

---

**Status**: ✅ Fully Implemented and Ready for Use (with Tesseract installed)

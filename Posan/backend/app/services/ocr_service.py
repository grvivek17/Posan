"""
OCR Service for extracting text from test papers.
Supports images (JPG, PNG) and PDFs using Tesseract OCR.
"""
import os
import re
import tempfile
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import cv2
import numpy as np
from PIL import Image
import pytesseract
import logging

logger = logging.getLogger(__name__)


class OCRService:
    """Service for OCR text extraction and test paper analysis."""
    
    def __init__(self):
        """Initialize OCR service with Tesseract configuration."""
        # Try to find Tesseract executable
        # Common Windows paths
        possible_paths = [
            r"C:\Program Files\Tesseract-OCR\tesseract.exe",
            r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
            # Add more paths as needed
        ]
        
        tesseract_cmd = None
        for path in possible_paths:
            if os.path.exists(path):
                tesseract_cmd = path
                break
        
        if tesseract_cmd:
            pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
            logger.info(f"Tesseract found at: {tesseract_cmd}")
        else:
            logger.warning("Tesseract path not found in common locations. Assuming it's in PATH.")
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray)
        
        # Apply adaptive thresholding for better text extraction
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Optional: Deskew (straighten) the image
        # This helps when the test paper is slightly tilted
        
        return thresh
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image file using OCR.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
        """
        try:
            # Load image
            image = cv2.imread(image_path)
            
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Preprocess for better OCR
            processed_image = self.preprocess_image(image)
            
            # Convert back to PIL Image for pytesseract
            pil_image = Image.fromarray(processed_image)
            
            # Extract text with custom config for better accuracy
            custom_config = r'--oem 3 --psm 6'  # LSTM OCR Engine, assume uniform block of text
            text = pytesseract.image_to_string(pil_image, config=custom_config)
            
            logger.info(f"Extracted {len(text)} characters from image")
            return text
            
        except Exception as e:
            logger.error(f"Error extracting text from image: {str(e)}")
            raise
    
    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """
        Extract text from a PDF file.
        Try pdfplumber first (best for digital PDFs), 
        fall back to OCR if needed.
        """
        all_text = []
        try:
            import pdfplumber
            with pdfplumber.open(pdf_path) as pdf:
                # Limit to first 20 pages for performance, especially for study material
                max_pages = min(len(pdf.pages), 20)
                for i in range(max_pages):
                    page = pdf.pages[i]
                    text = page.extract_text()
                    if text:
                        all_text.append(text)
            
            # If we got substantial text, return it
            content = "\n\n".join(all_text)
            if len(content.strip()) > 50:
                logger.info(f"Successfully extracted {len(content)} chars from {max_pages} pages using pdfplumber")
                return content
                
        except Exception as e:
            logger.warning(f"pdfplumber failed, trying pypdf: {e}")

        # Try pypdf (another digital PDF reader)
        try:
            from pypdf import PdfReader
            reader = PdfReader(pdf_path)
            pypdf_text = []
            max_pages = min(len(reader.pages), 20)
            for i in range(max_pages):
                page = reader.pages[i]
                text = page.extract_text()
                if text:
                    pypdf_text.append(text)
            
            content = "\n\n".join(pypdf_text)
            if len(content.strip()) > 50:
                logger.info(f"Successfully extracted {len(content)} chars from {max_pages} pages using pypdf")
                return content
        except Exception as e:
            logger.warning(f"pypdf failed: {e}")

        # Try fitz (PyMuPDF - very fast and reliable)
        try:
            import fitz
            doc = fitz.open(pdf_path)
            fitz_text = []
            max_pages = min(len(doc), 20)
            for i in range(max_pages):
                page = doc[i]
                text = page.get_text()
                if text:
                    fitz_text.append(text)
            
            content = "\n\n".join(fitz_text)
            if len(content.strip()) > 50:
                logger.info(f"Successfully extracted {len(content)} chars from {max_pages} pages using fitz")
                return content
        except Exception as e:
            logger.warning(f"fitz failed: {e}")

        # Fallback to OCR (for scanned PDFs) - Using fitz for image conversion to avoid Poppler dependency
        try:
            import fitz
            doc = fitz.open(pdf_path)
            ocr_text = []
            
            for i in range(len(doc)):
                page = doc.load_page(i)
                # Render page to an image (pixmap)
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72)) # 300 DPI
                
                # Convert pixmap to image bytes
                img_data = pix.tobytes("png")
                
                # Convert to numpy array for our image processor
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if img is not None:
                    processed_image = self.preprocess_image(img)
                    pil_image = Image.fromarray(processed_image)
                    text = pytesseract.image_to_string(pil_image, config=r'--oem 3 --psm 6')
                    ocr_text.append(text)
            
            combined_text = "\n\n".join(ocr_text)
            if len(combined_text.strip()) > 10:
                logger.info(f"Extracted {len(combined_text)} characters from PDF using fitz+OCR fallback")
                return combined_text
        except Exception as e:
            logger.error(f"OCR fallback failed: {e}")

        # Final return
        return "\n\n".join(all_text) if all_text else ""
    
    def extract_text(self, file_path: str, file_extension: str) -> str:
        """
        Extract text from file based on extension.
        
        Args:
            file_path: Path to file
            file_extension: File extension (.jpg, .png, .pdf)
            
        Returns:
            Extracted text
        """
        file_extension = file_extension.lower()
        
        if file_extension in ['.jpg', '.jpeg', '.png']:
            return self.extract_text_from_image(file_path)
        elif file_extension == '.pdf':
            return self.extract_text_from_pdf(file_path)
        else:
            raise ValueError(f"Unsupported file type: {file_extension}")
    
    def parse_test_scores(self, text: str) -> Dict[str, any]:
        """
        Parse test paper text to extract scores and marks.
        Uses pattern matching to find common test paper patterns.
        
        Args:
            text: Extracted text from OCR
            
        Returns:
            Dictionary with parsed information
        """
        # Initialize result
        result = {
            "total_score": None,
            "max_score": None,
            "questions_found": [],
            "marks_found": [],
            "confidence": "low"
        }
        
        # Pattern to find scores like "85/100", "Score: 75", "Marks: 42/50"
        score_patterns = [
            r'(\d+)\s*/\s*(\d+)',  # 85/100
            r'(?:score|marks|total)[:\s]+(\d+)\s*/\s*(\d+)',  # Score: 85/100
            r'(?:score|marks|total)[:\s]+(\d+)',  # Score: 85
        ]
        
        for pattern in score_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                if len(matches[0]) == 2:
                    # Format: 85/100
                    result["total_score"] = int(matches[0][0])
                    result["max_score"] = int(matches[0][1])
                    result["confidence"] = "high"
                    break
                elif len(matches[0]) == 1:
                    # Format: Score: 85 (no total)
                    result["total_score"] = int(matches[0][0])
                    result["max_score"] = 100  # Assume 100
                    result["confidence"] = "medium"
        
        # Look for question numbers and marks
        question_pattern = r'(?:Q|Question|#)\s*(\d+)[:\s]*.*?(?:(\d+)\s*(?:marks?|pts?|points?))?'
        question_matches = re.findall(question_pattern, text, re.IGNORECASE)
        
        if question_matches:
            result["questions_found"] = [int(q[0]) for q in question_matches if q[0]]
            result["marks_found"] = [int(q[1]) for q in question_matches if q[1]]
        
        # Try to identify subject
        subject_keywords = {
            "Mathematics": ["math", "algebra", "geometry", "calculus", "equation"],
            "Science": ["science", "physics", "chemistry", "biology", "experiment"],
            "English": ["english", "grammar", "essay", "reading", "comprehension"],
            "History": ["history", "civilization", "war", "dynasty"],
            "Geography": ["geography", "map", "continent", "country"]
        }
        
        detected_subject = None
        text_lower = text.lower()
        max_count = 0
        
        for subject, keywords in subject_keywords.items():
            count = sum(1 for keyword in keywords if keyword in text_lower)
            if count > max_count:
                max_count = count
                detected_subject = subject
        
        result["detected_subject"] = detected_subject
        
        return result
    
    def parse_question_answers(self, text: str, subject: str) -> List[Dict[str, any]]:
        """
        Parse test paper to extract question-answer pairs for detailed analysis.
        
        This method extracts:
        - Question text
        - Student's answer
        - Correct answer (if marked)
        - Marks awarded
        - Whether answer is correct/incorrect
        
        Args:
            text: Extracted text from OCR
            subject: Subject of the test
            
        Returns:
            List of question-answer dictionaries
        """
        questions = []
        lines = text.split('\n')
        
        current_question = None
        current_question_text = ""
        current_answer = ""
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Detect question start (Q1, Q2, Question 1, etc.)
            question_match = re.match(r'(?:Q|Question|#)[\s.]*(\\d+)[:\s.]*(.*)$', line, re.IGNORECASE)
            
            if question_match:
                # Save previous question if exists
                if current_question is not None:
                    questions.append(current_question)
                
                # Start new question
                question_number = int(question_match.group(1))
                question_text = question_match.group(2).strip()
                
                # Extract marks if present
                marks_match = re.search(r'\((\d+)\s*(?:marks?|pts?|points?)\)', line, re.IGNORECASE)
                marks = int(marks_match.group(1)) if marks_match else None
                
                current_question = {
                    "question_number": question_number,
                    "question_text": question_text,
                    "student_answer": "",
                    "correct_answer": None,
                    "marks_awarded": None,
                    "max_marks": marks,
                    "is_correct": None,
                    "feedback_marks": []  # ✓, ✗, checkmarks, crosses
                }
                current_question_text = question_text
                
            # Look for answer patterns
            elif current_question is not None:
                # Check for "Answer:" or "Ans:" pattern
                answer_match = re.match(r'(?:Answer|Ans|A)[:.\s]*(.+)$', line, re.IGNORECASE)
                
                if answer_match:
                    answer_text = answer_match.group(1).strip()
                    
                    # Check for correctness markers (✓, ✗, checkmarks, X, correct, wrong)
                    if '✓' in line or '✔' in line or 'correct' in line.lower():
                        current_question["is_correct"] = True
                        current_question["feedback_marks"].append("✓")
                    elif '✗' in line or '✘' in line or 'wrong' in line.lower() or 'incorrect' in line.lower():
                        current_question["is_correct"] = False
                        current_question["feedback_marks"].append("✗")
                    elif 'X' in line or '×' in line:
                        current_question["is_correct"] = False
                        current_question["feedback_marks"].append("✗")
                    
                    # Extract marks if shown (e.g., "5/10" or "5" marks)
                    marks_match = re.search(r'(\d+)\s*/\s*(\d+)', answer_text)
                    if marks_match:
                        current_question["marks_awarded"] = int(marks_match.group(1))
                        if current_question["max_marks"] is None:
                            current_question["max_marks"] = int(marks_match.group(2))
                    
                    current_question["student_answer"] = answer_text
                
                # Look for "Correct Answer:" pattern
                elif re.match(r'(?:Correct Answer|Correct|Solution)[:.\s]*(.+)$', line, re.IGNORECASE):
                    correct_match = re.match(r'(?:Correct Answer|Correct|Solution)[:.\s]*(.+)$', line, re.IGNORECASE)
                    current_question["correct_answer"] = correct_match.group(1).strip()
                
                # If it's just a continuation of question or answer text
                elif len(line) > 2:
                    if not current_question["student_answer"]:
                        # Might be continuation of question or the answer itself
                        # Check if it contains answer-like content
                        if any(indicator in line for indicator in ['=', ':', 'is', 'are', 'was', 'were']):
                            current_question["student_answer"] += " " + line
                    else:
                        current_question["student_answer"] += " " + line
        
        # Add the last question
        if current_question is not None:
            questions.append(current_question)
        
        # Post-process: Clean up and infer correctness if not marked
        for q in questions:
            # Clean up answer text
            q["student_answer"] = q["student_answer"].strip()
            
            # Remove marks notation from answer text
            q["student_answer"] = re.sub(r'\(\d+\s*(?:marks?|pts?|points?)\)', '', q["student_answer"]).strip()
            
            # If we have both student and correct answer but no correctness marker, compare them
            if (q["is_correct"] is None and q["student_answer"] and q["correct_answer"]):
                # Simple string comparison (case-insensitive, ignore extra spaces)
                student_clean = q["student_answer"].lower().strip()
                correct_clean = q["correct_answer"].lower().strip()
                q["is_correct"] = student_clean == correct_clean
        
        return questions
    

    def analyze_test_paper(
        self, 
        file_path: str, 
        file_extension: str,
        student_name: str,
        subject: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Complete test paper analysis pipeline with detailed question-answer extraction.
        
        Args:
            file_path: Path to uploaded file
            file_extension: File extension
            student_name: Student's name
            subject: Optional subject (if not provided, will try to detect)
            
        Returns:
            Analysis results including extracted text, parsed scores, and question-answer pairs
        """
        try:
            # Extract text using OCR
            extracted_text = self.extract_text(file_path, file_extension)
            
            # Parse scores and information
            parsed_data = self.parse_test_scores(extracted_text)
            
            # Use provided subject or detected subject
            final_subject = subject or parsed_data.get("detected_subject", "General")
            
            # Parse question-answer pairs for detailed analysis
            question_answers = self.parse_question_answers(extracted_text, final_subject)
            
            # Calculate statistics from parsed questions
            total_questions = len(question_answers)
            correct_answers = sum(1 for q in question_answers if q.get("is_correct") == True)
            incorrect_answers = sum(1 for q in question_answers if q.get("is_correct") == False)
            unanswered = sum(1 for q in question_answers if not q.get("student_answer"))
            
            # Calculate score from question analysis if not found in text
            if parsed_data.get("total_score") is None and question_answers:
                # Try to calculate from marks
                total_marks = sum(q.get("marks_awarded", 0) for q in question_answers if q.get("marks_awarded"))
                max_marks = sum(q.get("max_marks", 0) for q in question_answers if q.get("max_marks"))
                
                if total_marks > 0 or max_marks > 0:
                    parsed_data["total_score"] = total_marks
                    parsed_data["max_score"] = max_marks if max_marks > 0 else 100
            
            return {
                "success": True,
                "student_name": student_name,
                "subject": final_subject,
                "extracted_text": extracted_text,  # Full text for AI analysis
                "full_text_length": len(extracted_text),
                "score": parsed_data.get("total_score"),
                "total": parsed_data.get("max_score", 100),
                "confidence": parsed_data.get("confidence", "low"),
                "questions_found": total_questions,
                "correct_count": correct_answers,
                "incorrect_count": incorrect_answers,
                "unanswered_count": unanswered,
                "question_answers": question_answers,  # Detailed Q&A for AI analysis
                "parsing_info": parsed_data
            }
            
        except Exception as e:
            logger.error(f"Error analyzing test paper: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "student_name": student_name,
                "subject": subject or "Unknown"
            }


# Global OCR service instance
ocr_service = OCRService()

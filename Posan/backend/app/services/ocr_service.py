"""
OCR Service for extracting text from test papers.
Supports images (JPG, PNG) and PDFs using Tesseract OCR.

Enhanced with:
- EXIF orientation handling for phone camera photos
- Colored paper background handling (yellow, green, etc.)
- Red ink teacher marking filtering
- Auto-rotation and deskewing
- Improved question/answer parsing for Indian school papers
- Better score detection avoiding false positives
"""
import os
import re
import tempfile
import math
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import cv2
import numpy as np
from PIL import Image, ImageOps, ExifTags
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
    
    def fix_orientation_exif(self, pil_image: Image.Image) -> Image.Image:
        """
        Fix image orientation using EXIF data.
        Phone cameras embed rotation info in EXIF metadata,
        but cv2.imread ignores it, resulting in sideways images.
        Uses PIL's ImageOps.exif_transpose for robust handling.
        
        Args:
            pil_image: PIL Image object
            
        Returns:
            Correctly oriented PIL Image
        """
        try:
            fixed = ImageOps.exif_transpose(pil_image)
            if fixed.size != pil_image.size:
                logger.info(f"Applied EXIF orientation fix: {pil_image.size} -> {fixed.size}")
            return fixed
        except Exception as e:
            logger.warning(f"Could not apply EXIF orientation: {e}")
            return pil_image
    
    def detect_and_fix_rotation(self, image: np.ndarray) -> np.ndarray:
        """
        Detect if text is rotated and fix it using Tesseract OSD.
        Falls back to line-angle-based detection if OSD fails.
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Correctly rotated image
        """
        try:
            # Try Tesseract OSD (Orientation and Script Detection)
            pil_img = Image.fromarray(image)
            osd_data = pytesseract.image_to_osd(pil_img, output_type=pytesseract.Output.DICT)
            rotation_angle = osd_data.get('rotate', 0)
            confidence = osd_data.get('orientation_conf', 0)
            
            if rotation_angle != 0 and confidence > 1.0:
                logger.info(f"OSD detected rotation: {rotation_angle} degrees (confidence: {confidence})")
                # OSD 'rotate' = degrees to rotate CW to make upright
                if rotation_angle == 90:
                    image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
                elif rotation_angle == 180:
                    image = cv2.rotate(image, cv2.ROTATE_180)
                elif rotation_angle == 270:
                    image = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
        except Exception as e:
            logger.warning(f"OSD rotation detection failed: {e}")
            # Fallback: try line-based angle detection for deskewing
            try:
                image = self.deskew_image(image)
            except Exception as de:
                logger.warning(f"Deskew fallback also failed: {de}")
        
        return image
    
    def deskew_image(self, image: np.ndarray) -> np.ndarray:
        """
        Deskew a slightly tilted image using line detection.
        
        Args:
            image: Input image (grayscale or color)
            
        Returns:
            Deskewed image
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image.copy()
        
        # Use edge detection to find lines
        edges = cv2.Canny(gray, 50, 150, apertureSize=3)
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100,
                                minLineLength=100, maxLineGap=10)
        
        if lines is None or len(lines) == 0:
            return image
        
        # Calculate the dominant angle from detected lines
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 - x1 == 0:
                continue
            angle = math.degrees(math.atan2(y2 - y1, x2 - x1))
            # Only consider nearly horizontal lines (within 15 degrees)
            if abs(angle) < 15:
                angles.append(angle)
        
        if not angles:
            return image
        
        # Use the median angle to avoid outliers
        median_angle = np.median(angles)
        
        # Only deskew if the angle is significant but not too large
        if abs(median_angle) < 0.5 or abs(median_angle) > 10:
            return image
        
        logger.info(f"Deskewing by {median_angle:.2f} degrees")
        
        # Rotate to correct the skew
        (h, w) = image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, median_angle, 1.0)
        rotated = cv2.warpAffine(image, M, (w, h),
                                  flags=cv2.INTER_CUBIC,
                                  borderMode=cv2.BORDER_REPLICATE)
        return rotated
    
    def remove_colored_background(self, image: np.ndarray) -> np.ndarray:
        """
        Handle colored paper backgrounds (yellow, green, etc.)
        by converting to a clean grayscale with good contrast.
        
        Args:
            image: Input BGR color image
            
        Returns:
            Clean grayscale image with removed color cast
        """
        if len(image.shape) != 3:
            return image
        
        # Convert to LAB color space - L channel is luminance (brightness)
        # which is more robust to color variations than simple grayscale
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        l_channel = lab[:, :, 0]
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        # This dramatically improves contrast on colored paper
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(l_channel)
        
        return enhanced
    
    def filter_red_ink(self, image: np.ndarray) -> np.ndarray:
        """
        Optionally filter out red ink (teacher corrections/marks) 
        to avoid confusing OCR with overlapping text.
        
        This creates a mask of red regions and fills them with white.
        
        Args:
            image: Input BGR color image
            
        Returns:
            Image with red ink removed
        """
        if len(image.shape) != 3:
            return image
        
        hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        
        # Red color occupies two ranges in HSV (wraps around 0/180)
        # Lower red range
        lower_red1 = np.array([0, 70, 50])
        upper_red1 = np.array([10, 255, 255])
        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        
        # Upper red range
        lower_red2 = np.array([170, 70, 50])
        upper_red2 = np.array([180, 255, 255])
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        
        # Combine both red masks
        red_mask = mask1 | mask2
        
        # Dilate the mask slightly to cover edges of red marks
        kernel = np.ones((3, 3), np.uint8)
        red_mask = cv2.dilate(red_mask, kernel, iterations=1)
        
        # Replace red regions with white (background)
        result = image.copy()
        result[red_mask > 0] = [255, 255, 255]
        
        return result
    
    def preprocess_image(self, image: np.ndarray, keep_red_ink: bool = True) -> np.ndarray:
        """
        Preprocess image for better OCR accuracy.
        Enhanced pipeline for handling phone photos of colored school papers.
        
        Args:
            image: Input image as numpy array
            keep_red_ink: If True, keep red teacher marks; if False, filter them out
            
        Returns:
            Preprocessed image
        """
        if image is None:
            raise ValueError("Input image is None")
        
        original = image.copy()
        
        # Step 1: Handle colored paper background
        # Use LAB color space for better luminance extraction
        if len(image.shape) == 3:
            gray = self.remove_colored_background(image)
        else:
            gray = image
        
        # Step 2: Apply denoising
        denoised = cv2.fastNlMeansDenoising(gray, h=10)
        
        # Step 3: Apply adaptive thresholding with tuned parameters
        # Block size 15 and C=5 work better for phone photos than 11/2
        thresh = cv2.adaptiveThreshold(
            denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 15, 5
        )
        
        # Step 4: Light morphological cleaning to remove small noise dots
        kernel = np.ones((2, 2), np.uint8)
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        return cleaned
    
    def extract_text_from_image(self, image_path: str) -> str:
        """
        Extract text from an image file using OCR.
        Enhanced with EXIF orientation handling, auto-rotation detection,
        multi-pass OCR, and fallback rotation brute-force.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Extracted text
        """
        try:
            # Load image with PIL first to handle EXIF orientation
            pil_image = Image.open(image_path)
            pil_image = self.fix_orientation_exif(pil_image)
            
            # Convert PIL to OpenCV format (numpy array)
            image = np.array(pil_image)
            # PIL gives RGB, OpenCV needs BGR
            if len(image.shape) == 3 and image.shape[2] == 3:
                image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            elif len(image.shape) == 3 and image.shape[2] == 4:
                image = cv2.cvtColor(image, cv2.COLOR_RGBA2BGR)
            
            if image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            # Resize large phone photos for performance (max 1800px on longest side)
            # Higher resolution helps with OCR accuracy on colored paper
            h, w = image.shape[:2]
            max_dim = 1800
            scale = min(max_dim / max(h, w), 1.0)
            if scale < 1.0:
                image = cv2.resize(image, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
                logger.info(f"Resized image from {w}x{h} to {image.shape[1]}x{image.shape[0]}")
            
            # Helper: run OCR on an image and return (text, alpha_count)
            def try_ocr(img, config='--oem 3 --psm 4'):
                if len(img.shape) == 3:
                    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                else:
                    gray = img
                text = pytesseract.image_to_string(Image.fromarray(gray), config=config)
                alpha = sum(1 for c in text if c.isalnum())
                return text, alpha
            
            def try_ocr_preprocessed(img, config='--oem 3 --psm 4'):
                """OCR with LAB+CLAHE preprocessing for colored paper."""
                processed = self.preprocess_image(img)
                text = pytesseract.image_to_string(Image.fromarray(processed), config=config)
                alpha = sum(1 for c in text if c.isalnum())
                return text, alpha
            
            # Step 1: Try OCR on current orientation (after EXIF fix)
            best_text, best_alpha = try_ocr(image)
            logger.info(f"Initial OCR: {best_alpha} alphanumeric chars")
            
            # Step 2: If poor result, try OSD-based rotation detection
            if best_alpha < 100:
                try:
                    gray_for_osd = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
                    osd_data = pytesseract.image_to_osd(
                        Image.fromarray(gray_for_osd), output_type=pytesseract.Output.DICT
                    )
                    rotation_angle = osd_data.get('rotate', 0)
                    osd_conf = osd_data.get('orientation_conf', 0)
                    
                    if rotation_angle != 0 and osd_conf > 1.0:
                        logger.info(f"OSD detected rotation={rotation_angle}, confidence={osd_conf}")
                        if rotation_angle == 90:
                            rotated = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)
                        elif rotation_angle == 180:
                            rotated = cv2.rotate(image, cv2.ROTATE_180)
                        elif rotation_angle == 270:
                            rotated = cv2.rotate(image, cv2.ROTATE_90_COUNTERCLOCKWISE)
                        else:
                            rotated = image
                        
                        osd_text, osd_alpha = try_ocr(rotated)
                        if osd_alpha > best_alpha:
                            best_text, best_alpha = osd_text, osd_alpha
                            image = rotated  # Update image for further processing
                            logger.info(f"OSD rotation improved: {osd_alpha} alphanumeric chars")
                except Exception as e:
                    logger.warning(f"OSD rotation detection failed: {e}")
            
            # Step 3: If still poor, brute-force all rotations
            if best_alpha < 100:
                for rot_name, rot_code in [
                    ('90CW', cv2.ROTATE_90_CLOCKWISE),
                    ('90CCW', cv2.ROTATE_90_COUNTERCLOCKWISE),
                    ('180', cv2.ROTATE_180)
                ]:
                    rotated = cv2.rotate(image, rot_code)
                    rot_text, rot_alpha = try_ocr(rotated)
                    if rot_alpha > best_alpha:
                        best_text, best_alpha = rot_text, rot_alpha
                        image = rotated
                        logger.info(f"Brute-force {rot_name} improved: {rot_alpha} alphanumeric chars")
            
            # Step 4: Try preprocessed version (LAB+CLAHE) for colored paper
            try:
                proc_text, proc_alpha = try_ocr_preprocessed(image)
                if proc_alpha > best_alpha:
                    best_text, best_alpha = proc_text, proc_alpha
                    logger.info(f"Preprocessed OCR improved: {proc_alpha} alphanumeric chars")
            except Exception as e:
                logger.warning(f"Preprocessed OCR failed: {e}")
            
            # Step 5: Try with red ink filtered out
            try:
                no_red = self.filter_red_ink(image)
                no_red_text, no_red_alpha = try_ocr(no_red)
                if no_red_alpha > best_alpha:
                    best_text, best_alpha = no_red_text, no_red_alpha
                    logger.info(f"Red-ink-filtered OCR improved: {no_red_alpha} alphanumeric chars")
            except Exception:
                pass
            
            logger.info(f"Final OCR result: {len(best_text)} chars ({best_alpha} alphanumeric)")
            return best_text
            
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
                    text = pytesseract.image_to_string(pil_image, config=r'--oem 3 --psm 3')
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
        Enhanced to avoid false positives from marking notation 
        like (25x1=25), (10x1=10), (5x2=10), etc.
        
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
        
        # First, try to find explicit score labels 
        # These are most reliable: "Score: 85/100", "Marks: 42/50", "Total: 75/100"
        labeled_score_patterns = [
            r'(?:score|marks\s*obtained|total\s*marks|result)[:\s]+(\d+)\s*/\s*(\d+)',
            r'(?:score|marks\s*obtained|total\s*marks|result)[:\s]+(\d+)\s+(?:out\s+of|from)\s+(\d+)',
        ]
        
        for pattern in labeled_score_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                score = int(matches[0][0])
                total = int(matches[0][1])
                # Validate: score should be <= total, total should be reasonable
                if 0 <= score <= total <= 500:
                    result["total_score"] = score
                    result["max_score"] = total
                    result["confidence"] = "high"
                    break
        
        # If no labeled score found, try to find from header info
        # Look for "MARKS : 50" or "MARKS : 30" type patterns (total marks of the paper)
        if result["total_score"] is None:
            header_marks = re.findall(
                r'(?:MARKS|MAX\.?\s*MARKS|TOTAL\s*MARKS)\s*[:\s]+(\d+)',
                text, re.IGNORECASE
            )
            if header_marks:
                result["max_score"] = int(header_marks[0])
                result["confidence"] = "low"  # We know the total but not the score
        
        # Avoid matching marking notation patterns like (25x1=25), (10x1=10), (5x2=10)
        # These appear in the paper headers and are NOT the student's score
        
        # Try to find simple X/Y score only if NOT preceded by marking notation
        if result["total_score"] is None:
            # Match N/M but exclude patterns like "25x1=25" or "5x2=10" or option numbers
            potential_scores = re.findall(
                r'(?<![x×\d])(\d{1,3})\s*/\s*(\d{1,3})(?!\s*(?:marks?|pts?|questions?))',
                text, re.IGNORECASE
            )
            
            for match in potential_scores:
                score = int(match[0])
                total = int(match[1])
                # Validate: reasonable score range, not a question option
                if 0 <= score <= total <= 200 and total >= 10:
                    result["total_score"] = score
                    result["max_score"] = total
                    result["confidence"] = "medium"
                    break
        
        # Look for question numbers and marks
        # Support patterns like "1.", "2.", "Q1", "#1", etc.
        question_pattern = r'(?:^|\n)\s*(?:Q|Question|#)?\s*(\d+)\s*[.):]\s*'
        question_matches = re.findall(question_pattern, text, re.IGNORECASE | re.MULTILINE)
        
        if question_matches:
            result["questions_found"] = sorted(set(int(q) for q in question_matches))
        
        # Try to identify subject from text content
        subject_keywords = {
            "Mathematics": ["math", "algebra", "geometry", "calculus", "equation", "subtract",
                           "multiply", "divide", "addition", "numeral", "thousands", "hundreds",
                           "successor", "product", "sum", "difference"],
            "Science": ["science", "physics", "chemistry", "biology", "experiment", "photosynthesis",
                       "stomata", "chlorophyll", "aquatic", "habitat", "plant", "animal"],
            "English": ["english", "grammar", "essay", "reading", "comprehension", "passage",
                       "noun", "verb", "adjective", "pronoun", "story", "poem"],
            "EVS": ["evs", "environmental", "climbers", "sense organs", "aquatic", "burrows",
                   "habitat", "plants", "animals", "food", "shelter"],
            "History": ["history", "civilization", "war", "dynasty", "emperor", "kingdom"],
            "Geography": ["geography", "map", "continent", "country", "river", "mountain"]
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
        Enhanced to handle Indian school paper formats:
        - MCQ with options a/b/c/d
        - Fill in the blanks
        - Short answer questions
        - Number-only question labels (1., 2., etc.)
        - Tick marks and handwritten answers
        
        Args:
            text: Extracted text from OCR
            subject: Subject of the test
            
        Returns:
            List of question-answer dictionaries
        """
        questions = []
        lines = text.split('\n')
        
        current_question = None
        current_options = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            if not line:
                continue
            
            # Detect question start - enhanced patterns for Indian school papers
            # Matches: "1.", "1)", "Q1:", "Q.1", "Question 1", "#1", "I.", "II.", "i.", "ii." etc.
            # Tolerant of leading OCR noise characters
            question_match = re.match(
                r'^[^a-zA-Z0-9]*(?:'
                r'(?:Q|Question)\s*[.:]?\s*(\d+)'  # Q1, Question 1
                r'|#\s*(\d+)'                        # #1
                r'|(\d{1,2})\s*[.,)]\s+'             # 1. or 1) or 1, followed by space
                r'|([ivxlcIVXLC]+)\s*[.,)]\s+'       # Roman numerals (upper or lower)
                r')'
                r'(.*)$',
                line, re.IGNORECASE
            )
            
            if question_match:
                groups = question_match.groups()
                # Find which group matched
                question_number = None
                question_text = groups[-1].strip() if groups[-1] else ""
                
                for g in groups[:-1]:
                    if g is not None:
                        # Convert roman numerals to numbers (upper or lowercase)
                        g_upper = g.upper()
                        if re.match(r'^[IVXLC]+$', g_upper):
                            roman_map = {'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
                                        'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10}
                            question_number = roman_map.get(g_upper, None)
                            if question_number is None:
                                try:
                                    question_number = int(g)
                                except ValueError:
                                    continue
                        else:
                            try:
                                question_number = int(g)
                            except ValueError:
                                continue
                        break
                
                if question_number is None:
                    continue
                
                # Skip if this looks like a sub-option (a), b), c), d))
                if re.match(r'^[a-d]\)', line, re.IGNORECASE):
                    continue
                
                # Skip section headers like "I. Choose the correct answer:"
                if any(header_word in question_text.lower() for header_word in [
                    'choose the correct', 'fill in the blank', 'answer the following',
                    'match the following', 'read the passage', 'name the following',
                    'complete the analogy', 'picture based', 'answer in short'
                ]):
                    continue
                
                # Save previous question if exists
                if current_question is not None:
                    # Attach collected options
                    if current_options:
                        current_question["options"] = current_options
                    questions.append(current_question)
                
                # Extract marks if present in line
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
                    "feedback_marks": [],
                    "options": [],
                    "question_type": "unknown"
                }
                current_options = []
                
                # Detect question type from content
                if any(word in question_text.lower() for word in ['fill in', 'blank', '___', '____']):
                    current_question["question_type"] = "fill_in_blank"
                elif 'choose' in question_text.lower() or 'correct answer' in question_text.lower():
                    current_question["question_type"] = "mcq"
                
                continue
            
            # Detect MCQ options: a), b), c), d) or a., b., c., d.
            option_match = re.match(
                r'^([a-d])\s*[.)]\s*(.+)$',
                line, re.IGNORECASE
            )
            
            if option_match and current_question is not None:
                option_label = option_match.group(1).lower()
                option_text = option_match.group(2).strip()
                current_options.append({
                    "label": option_label,
                    "text": option_text
                })
                current_question["question_type"] = "mcq"
                
                # Check for selection markers (tick, circle, underline indicators)
                # In OCR text, selected answers might have extra marks
                if '✓' in line or '✔' in line or 'V' in line:
                    current_question["student_answer"] = option_text
                    current_question["is_correct"] = True
                    current_question["feedback_marks"].append("✓")
                elif '✗' in line or '✘' in line:
                    current_question["student_answer"] = option_text
                    current_question["is_correct"] = False
                    current_question["feedback_marks"].append("✗")
                
                continue
            
            # Look for answer patterns  
            if current_question is not None:
                # Check for "Answer:" or "Ans:" pattern
                answer_match = re.match(r'(?:Answer|Ans|A)\s*[:.\s]+(.+)$', line, re.IGNORECASE)
                
                if answer_match:
                    answer_text = answer_match.group(1).strip()
                    current_question["student_answer"] = answer_text
                    
                    # Check for correctness markers
                    if '✓' in line or '✔' in line or 'correct' in line.lower():
                        current_question["is_correct"] = True
                        current_question["feedback_marks"].append("✓")
                    elif '✗' in line or '✘' in line or 'wrong' in line.lower() or 'incorrect' in line.lower():
                        current_question["is_correct"] = False
                        current_question["feedback_marks"].append("✗")
                    
                    # Extract marks if shown
                    marks_match = re.search(r'(\d+)\s*/\s*(\d+)', answer_text)
                    if marks_match:
                        current_question["marks_awarded"] = int(marks_match.group(1))
                        if current_question["max_marks"] is None:
                            current_question["max_marks"] = int(marks_match.group(2))
                
                # Look for "Correct Answer:" pattern
                elif re.match(r'(?:Correct Answer|Correct|Solution)\s*[:.\s]+(.+)$', line, re.IGNORECASE):
                    correct_match = re.match(r'(?:Correct Answer|Correct|Solution)\s*[:.\s]+(.+)$', line, re.IGNORECASE)
                    current_question["correct_answer"] = correct_match.group(1).strip()
                
                # Continuation of question or answer text
                elif len(line) > 2 and not re.match(r'^[a-d]\)', line, re.IGNORECASE):
                    if not current_question["student_answer"]:
                        if any(indicator in line for indicator in ['=', ':']):
                            current_question["student_answer"] += " " + line
                    else:
                        current_question["student_answer"] += " " + line
        
        # Add the last question
        if current_question is not None:
            if current_options:
                current_question["options"] = current_options
            questions.append(current_question)
        
        # Post-process: Clean up and infer correctness if not marked
        for q in questions:
            # Clean up answer text
            q["student_answer"] = q["student_answer"].strip()
            
            # Remove marks notation from answer text
            q["student_answer"] = re.sub(r'\(\d+\s*(?:marks?|pts?|points?)\)', '', q["student_answer"]).strip()
            
            # If we have both student and correct answer but no correctness marker, compare them
            if (q["is_correct"] is None and q["student_answer"] and q["correct_answer"]):
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

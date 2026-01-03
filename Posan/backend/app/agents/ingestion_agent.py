"""
Ingestion Agent - Enhanced PDF/Image Processing with Intelligent Chunking

Responsibilities:
- Extract text from PDFs and images
- Perform OCR for scanned/handwritten content
- Intelligent chunking (500-800 tokens)
- Topic extraction and tagging
- Section/heading metadata attachment
"""

import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import logging

from app.agents import AgentBase
from app.services.ocr_service import ocr_service

logger = logging.getLogger(__name__)


class IngestionAgent(AgentBase):
    """
    Agent for ingesting and processing study materials.
    
    Features:
    - Multi-format support (PDF, images)
    - OCR fallback for scanned content
    - Intelligent chunking with overlap
    - Topic extraction
    - Metadata enrichment
    """
    
    def __init__(self):
        super().__init__(name="ingestion", max_retries=2)
        self.chunk_size = 700  # Target tokens per chunk
        self.chunk_overlap = 100  # Overlap between chunks
        self.min_chunk_size = 200  # Minimum chunk size
    
    def _execute_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute ingestion task.
        
        Input:
            - file_path: Path to file
            - file_extension: File extension (.pdf, .jpg, .png)
            - material_id: Material ID for tracking
            - subject: Optional subject hint
            - grade: Optional grade level
            
        Output:
            - chunks: List of text chunks with metadata
            - total_chunks: Number of chunks created
            - total_tokens: Approximate total tokens
            - topics: Extracted topics
            - metadata: Additional metadata
        """
        file_path = input_data.get("file_path")
        file_extension = input_data.get("file_extension", "").lower()
        material_id = input_data.get("material_id")
        subject = input_data.get("subject")
        grade = input_data.get("grade")
        
        if not file_path:
            raise ValueError("file_path is required")
        
        self.logger.info(f"Ingesting file: {file_path}")
        
        # Step 1: Extract raw text
        raw_text = self._extract_text(file_path, file_extension)
        
        if not raw_text or len(raw_text.strip()) < 10:
            raise ValueError(f"Insufficient text extracted from file: {len(raw_text)} characters")
        
        self.logger.info(f"Extracted {len(raw_text)} characters")
        
        # Step 2: Detect structure (headings, sections)
        structure = self._detect_structure(raw_text)
        
        # Step 3: Create intelligent chunks
        chunks = self._create_chunks(
            text=raw_text,
            structure=structure,
            material_id=material_id,
            subject=subject,
            grade=grade
        )
        
        # Step 4: Extract topics from chunks
        topics = self._extract_topics(chunks)
        
        # Step 5: Calculate statistics
        total_tokens = sum(chunk["tokens"] for chunk in chunks)
        
        return {
            "chunks": chunks,
            "total_chunks": len(chunks),
            "total_tokens": total_tokens,
            "topics": topics,
            "metadata": {
                "raw_text_length": len(raw_text),
                "has_structure": len(structure["headings"]) > 0,
                "subject": subject,
                "grade": grade
            }
        }
    
    def _extract_text(self, file_path: str, file_extension: str) -> str:
        """
        Extract text from file using OCR service.
        
        Args:
            file_path: Path to file
            file_extension: File extension
            
        Returns:
            Extracted text
        """
        try:
            text = ocr_service.extract_text(file_path, file_extension)
            return text
        except Exception as e:
            self.logger.error(f"Text extraction failed: {e}")
            raise
    
    def _detect_structure(self, text: str) -> Dict[str, Any]:
        """
        Detect document structure (headings, sections, lists).
        
        Args:
            text: Raw text
            
        Returns:
            Structure information with headings and sections
        """
        lines = text.split('\n')
        structure = {
            "headings": [],
            "sections": [],
            "lists": []
        }
        
        current_section = None
        section_start_line = 0
        
        for line_idx, line in enumerate(lines):
            line_stripped = line.strip()
            
            if not line_stripped:
                continue
            
            # Detect headings (all caps, short lines, numbered sections)
            is_heading = False
            heading_level = 0
            
            # Pattern 1: ALL CAPS (likely heading)
            if line_stripped.isupper() and len(line_stripped) < 100:
                is_heading = True
                heading_level = 1
            
            # Pattern 2: Numbered sections (1., 1.1, Chapter 1, etc.)
            elif re.match(r'^(?:Chapter|Section|Unit|Lesson)\s+\d+', line_stripped, re.IGNORECASE):
                is_heading = True
                heading_level = 1
            
            # Pattern 3: Simple numbering (1., 2., etc.) at start of line
            elif re.match(r'^\d+\.?\s+[A-Z]', line_stripped):
                is_heading = True
                heading_level = 2
            
            if is_heading:
                # Save previous section if exists
                if current_section:
                    structure["sections"].append({
                        "heading": current_section,
                        "start_line": section_start_line,
                        "end_line": line_idx - 1
                    })
                
                # Start new section
                current_section = line_stripped
                section_start_line = line_idx
                
                structure["headings"].append({
                    "text": line_stripped,
                    "line": line_idx,
                    "level": heading_level
                })
            
            # Detect lists (bullet points, numbered lists)
            if re.match(r'^[\-\*•]\s+', line_stripped) or re.match(r'^\d+[\.\)]\s+', line_stripped):
                structure["lists"].append({
                    "line": line_idx,
                    "text": line_stripped
                })
        
        # Add final section
        if current_section:
            structure["sections"].append({
                "heading": current_section,
                "start_line": section_start_line,
                "end_line": len(lines) - 1
            })
        
        self.logger.info(
            f"Detected structure: {len(structure['headings'])} headings, "
            f"{len(structure['sections'])} sections"
        )
        
        return structure
    
    def _create_chunks(
        self,
        text: str,
        structure: Dict[str, Any],
        material_id: Optional[str] = None,
        subject: Optional[str] = None,
        grade: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Create intelligent chunks with metadata.
        
        Args:
            text: Raw text
            structure: Document structure
            material_id: Material ID
            subject: Subject hint
            grade: Grade level
            
        Returns:
            List of chunks with metadata
        """
        chunks = []
        
        # If we have sections, chunk by section
        if structure["sections"]:
            chunks = self._chunk_by_sections(text, structure, material_id, subject, grade)
        else:
            # Fallback: chunk by token count
            chunks = self._chunk_by_tokens(text, material_id, subject, grade)
        
        # Assign chunk indices
        for idx, chunk in enumerate(chunks):
            chunk["chunk_index"] = idx
        
        return chunks
    
    def _chunk_by_sections(
        self,
        text: str,
        structure: Dict[str, Any],
        material_id: Optional[str],
        subject: Optional[str],
        grade: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Chunk text based on detected sections."""
        lines = text.split('\n')
        chunks = []
        
        for section in structure["sections"]:
            section_lines = lines[section["start_line"]:section["end_line"] + 1]
            section_text = '\n'.join(section_lines)
            
            # Estimate tokens (rough: 1 token ≈ 4 characters)
            tokens = len(section_text) // 4
            
            # If section is too large, split it
            if tokens > self.chunk_size * 1.5:
                sub_chunks = self._split_large_section(
                    section_text,
                    section["heading"],
                    material_id,
                    subject,
                    grade
                )
                chunks.extend(sub_chunks)
            else:
                chunks.append({
                    "text": section_text,
                    "tokens": tokens,
                    "heading": section["heading"],
                    "topic": self._extract_topic_from_heading(section["heading"]),
                    "material_id": material_id,
                    "subject": subject,
                    "grade": grade,
                    "metadata": {
                        "section_start": section["start_line"],
                        "section_end": section["end_line"]
                    }
                })
        
        return chunks
    
    def _chunk_by_tokens(
        self,
        text: str,
        material_id: Optional[str],
        subject: Optional[str],
        grade: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Chunk text by token count with overlap."""
        chunks = []
        
        # Split into sentences (rough approximation)
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        current_chunk = []
        current_tokens = 0
        
        for sentence in sentences:
            sentence_tokens = len(sentence) // 4
            
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = ' '.join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "tokens": current_tokens,
                    "heading": None,
                    "topic": None,
                    "material_id": material_id,
                    "subject": subject,
                    "grade": grade,
                    "metadata": {}
                })
                
                # Start new chunk with overlap
                overlap_sentences = current_chunk[-2:] if len(current_chunk) >= 2 else current_chunk
                current_chunk = overlap_sentences + [sentence]
                current_tokens = sum(len(s) // 4 for s in current_chunk)
            else:
                current_chunk.append(sentence)
                current_tokens += sentence_tokens
        
        # Add final chunk
        if current_chunk:
            chunk_text = ' '.join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "tokens": current_tokens,
                "heading": None,
                "topic": None,
                "material_id": material_id,
                "subject": subject,
                "grade": grade,
                "metadata": {}
            })
        
        return chunks
    
    def _split_large_section(
        self,
        text: str,
        heading: str,
        material_id: Optional[str],
        subject: Optional[str],
        grade: Optional[int]
    ) -> List[Dict[str, Any]]:
        """Split a large section into smaller chunks."""
        # Use token-based chunking for the section
        sub_chunks = self._chunk_by_tokens(text, material_id, subject, grade)
        
        # Add heading to all sub-chunks
        for chunk in sub_chunks:
            chunk["heading"] = heading
            chunk["topic"] = self._extract_topic_from_heading(heading)
        
        return sub_chunks
    
    def _extract_topic_from_heading(self, heading: str) -> Optional[str]:
        """Extract topic from heading text."""
        if not heading:
            return None
        
        # Remove common prefixes
        topic = re.sub(r'^(?:Chapter|Section|Unit|Lesson)\s+\d+[:\s]*', '', heading, flags=re.IGNORECASE)
        topic = topic.strip()
        
        # Remove numbering
        topic = re.sub(r'^\d+\.?\s*', '', topic)
        
        return topic if topic else None
    
    def _extract_topics(self, chunks: List[Dict[str, Any]]) -> List[str]:
        """
        Extract unique topics from chunks.
        
        Args:
            chunks: List of chunks
            
        Returns:
            List of unique topics
        """
        topics = set()
        
        for chunk in chunks:
            if chunk.get("topic"):
                topics.add(chunk["topic"])
        
        # If no topics from headings, try to extract from text
        if not topics:
            for chunk in chunks[:5]:  # Check first 5 chunks
                text = chunk["text"]
                # Look for capitalized phrases (potential topics)
                matches = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3}\b', text)
                topics.update(matches[:3])  # Add up to 3 topics per chunk
        
        return sorted(list(topics))[:10]  # Return top 10 topics


# Global ingestion agent instance
ingestion_agent = IngestionAgent()

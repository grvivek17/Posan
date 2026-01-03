"""
Question Generator Agent - AI-Powered Practice Question Generation

Responsibilities:
- Generate practice questions from text chunks
- Support multiple question types (MCQ, short-answer, fill-in-the-blank)
- Grade-appropriate vocabulary and difficulty
- Automatic answer and hint generation
- Integration with retrieval agent for context
"""

from typing import Dict, Any, List, Optional
import logging
import random
import re

from app.agents import AgentBase
from app.services.ai_content import AIContentGenerator

logger = logging.getLogger(__name__)


class QuestionGeneratorAgent(AgentBase):
    """
    Agent for generating practice questions from study materials.
    
    Features:
    - Multiple question types (MCQ, short-answer, fill-in-the-blank)
    - Grade-appropriate content
    - Automatic answer generation
    - Hints and explanations
    - Difficulty levels
    """
    
    def __init__(self):
        super().__init__(name="question_generator", max_retries=2)
        self.ai_generator = AIContentGenerator()
    
    def _execute_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute question generation task.
        
        Input:
            - operation: "generate_questions" or "generate_practice_set"
            - chunks: List of text chunks (for generate_questions)
            - context: Text context (alternative to chunks)
            - grade: Grade level (1-8)
            - subject: Subject area
            - question_types: List of types ["mcq", "short_answer", "fill_blank"]
            - count: Number of questions to generate
            - difficulty: "easy", "medium", "hard"
            
        Output:
            - questions: List of question objects
            - count: Number of questions generated
            - metadata: Additional information
        """
        operation = input_data.get("operation", "generate_questions")
        
        if operation == "generate_questions":
            return self._generate_questions(input_data)
        elif operation == "generate_practice_set":
            return self._generate_practice_set(input_data)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def _generate_questions(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate questions from chunks or context"""
        chunks = input_data.get("chunks", [])
        context = input_data.get("context", "")
        grade = input_data.get("grade", 5)
        subject = input_data.get("subject", "General")
        question_types = input_data.get("question_types", ["mcq", "short_answer"])
        count = input_data.get("count", 5)
        difficulty = input_data.get("difficulty", "medium")
        
        # Build context from chunks if provided
        if chunks and not context:
            context = "\n\n".join([
                chunk.get("text", "") for chunk in chunks[:5]  # Use top 5 chunks
            ])
        
        if not context:
            raise ValueError("Either 'chunks' or 'context' is required")
        
        self.logger.info(
            f"Generating {count} questions for grade {grade}, subject: {subject}"
        )
        
        # Generate questions using AI
        questions = []
        
        # Distribute question types
        type_distribution = self._distribute_question_types(question_types, count)
        
        for q_type, q_count in type_distribution.items():
            if q_count > 0:
                generated = self._generate_by_type(
                    context=context,
                    question_type=q_type,
                    count=q_count,
                    grade=grade,
                    subject=subject,
                    difficulty=difficulty
                )
                questions.extend(generated)
        
        # Shuffle questions
        random.shuffle(questions)
        
        # Add question IDs
        for idx, question in enumerate(questions, 1):
            question["id"] = f"q_{idx}"
            question["question_number"] = idx
        
        return {
            "questions": questions,
            "count": len(questions),
            "metadata": {
                "grade": grade,
                "subject": subject,
                "difficulty": difficulty,
                "context_length": len(context)
            }
        }
    
    def _generate_practice_set(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a complete practice set with metadata"""
        result = self._generate_questions(input_data)
        
        # Add practice set metadata
        title = input_data.get("title", f"{input_data.get('subject', 'General')} Practice")
        
        return {
            "title": title,
            "description": f"Practice questions for grade {input_data.get('grade', 5)}",
            **result
        }
    
    def _distribute_question_types(
        self,
        question_types: List[str],
        total_count: int
    ) -> Dict[str, int]:
        """Distribute question count across types"""
        if not question_types:
            question_types = ["mcq"]
        
        distribution = {}
        per_type = total_count // len(question_types)
        remainder = total_count % len(question_types)
        
        for q_type in question_types:
            distribution[q_type] = per_type
        
        # Distribute remainder
        for i in range(remainder):
            distribution[question_types[i]] += 1
        
        return distribution
    
    def _generate_by_type(
        self,
        context: str,
        question_type: str,
        count: int,
        grade: int,
        subject: str,
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Generate questions of a specific type"""
        if question_type == "mcq":
            return self._generate_mcq(context, count, grade, subject, difficulty)
        elif question_type == "short_answer":
            return self._generate_short_answer(context, count, grade, subject, difficulty)
        elif question_type == "fill_blank":
            return self._generate_fill_blank(context, count, grade, subject, difficulty)
        else:
            self.logger.warning(f"Unknown question type: {question_type}, using MCQ")
            return self._generate_mcq(context, count, grade, subject, difficulty)
    
    def _generate_mcq(
        self,
        context: str,
        count: int,
        grade: int,
        subject: str,
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Generate multiple choice questions"""
        prompt = f"""Based on this {subject} content for grade {grade} students, create {count} multiple choice questions.

Content:
{context[:1500]}

Requirements:
- Difficulty: {difficulty}
- 4 options per question (A, B, C, D)
- Only one correct answer
- Age-appropriate vocabulary for grade {grade}
- Include a brief hint for each question

Format each question as:
Q: [question text]
A) [option]
B) [option]
C) [option]
D) [option]
Answer: [correct letter]
Hint: [helpful hint]
---"""
        
        response = self.ai_generator._generate_text(prompt, max_tokens=800)
        
        # Parse response into structured questions
        questions = self._parse_mcq_response(response, subject, difficulty)
        
        return questions[:count]
    
    def _generate_short_answer(
        self,
        context: str,
        count: int,
        grade: int,
        subject: str,
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Generate short answer questions"""
        prompt = f"""Based on this {subject} content for grade {grade} students, create {count} short answer questions.

Content:
{context[:1500]}

Requirements:
- Difficulty: {difficulty}
- Questions should require 1-3 sentence answers
- Age-appropriate for grade {grade}
- Include expected answer and a hint

Format each question as:
Q: [question text]
Expected Answer: [1-3 sentences]
Hint: [helpful hint]
---"""
        
        response = self.ai_generator._generate_text(prompt, max_tokens=600)
        
        # Parse response
        questions = self._parse_short_answer_response(response, subject, difficulty)
        
        return questions[:count]
    
    def _generate_fill_blank(
        self,
        context: str,
        count: int,
        grade: int,
        subject: str,
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Generate fill-in-the-blank questions"""
        prompt = f"""Based on this {subject} content for grade {grade} students, create {count} fill-in-the-blank questions.

Content:
{context[:1500]}

Requirements:
- Difficulty: {difficulty}
- Use _____ for the blank
- Age-appropriate for grade {grade}
- Include the answer and a hint

Format each question as:
Q: [sentence with _____ for blank]
Answer: [word or phrase]
Hint: [helpful hint]
---"""
        
        response = self.ai_generator._generate_text(prompt, max_tokens=500)
        
        # Parse response
        questions = self._parse_fill_blank_response(response, subject, difficulty)
        
        return questions[:count]
    
    def _parse_mcq_response(
        self,
        response: str,
        subject: str,
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Parse MCQ response into structured format"""
        questions = []
        
        # Split by question separator
        parts = response.split("---")
        
        for part in parts:
            part = part.strip()
            if not part or len(part) < 20:
                continue
            
            try:
                # Extract question
                q_match = re.search(r'Q:\s*(.+?)(?=\n[A-D]\))', part, re.DOTALL)
                if not q_match:
                    continue
                
                question_text = q_match.group(1).strip()
                
                # Extract options
                options = {}
                for letter in ['A', 'B', 'C', 'D']:
                    opt_match = re.search(
                        rf'{letter}\)\s*(.+?)(?=\n[A-D]\)|Answer:|Hint:|$)',
                        part,
                        re.DOTALL
                    )
                    if opt_match:
                        options[letter] = opt_match.group(1).strip()
                
                # Extract answer
                ans_match = re.search(r'Answer:\s*([A-D])', part)
                correct_answer = ans_match.group(1) if ans_match else 'A'
                
                # Extract hint
                hint_match = re.search(r'Hint:\s*(.+?)(?=---|$)', part, re.DOTALL)
                hint = hint_match.group(1).strip() if hint_match else "Think carefully about the question."
                
                if len(options) >= 3:  # At least 3 options
                    questions.append({
                        "type": "mcq",
                        "question": question_text,
                        "options": options,
                        "correct_answer": correct_answer,
                        "hint": hint,
                        "subject": subject,
                        "difficulty": difficulty
                    })
            
            except Exception as e:
                self.logger.warning(f"Failed to parse MCQ: {e}")
                continue
        
        # Fallback: create at least one question
        if not questions:
            questions.append(self._create_fallback_mcq(subject, difficulty))
        
        return questions
    
    def _parse_short_answer_response(
        self,
        response: str,
        subject: str,
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Parse short answer response"""
        questions = []
        parts = response.split("---")
        
        for part in parts:
            part = part.strip()
            if not part or len(part) < 20:
                continue
            
            try:
                # Extract question
                q_match = re.search(r'Q:\s*(.+?)(?=Expected Answer:|Answer:|Hint:)', part, re.DOTALL)
                if not q_match:
                    continue
                
                question_text = q_match.group(1).strip()
                
                # Extract answer
                ans_match = re.search(
                    r'(?:Expected Answer|Answer):\s*(.+?)(?=Hint:|$)',
                    part,
                    re.DOTALL
                )
                answer = ans_match.group(1).strip() if ans_match else "Answer not provided"
                
                # Extract hint
                hint_match = re.search(r'Hint:\s*(.+?)(?=---|$)', part, re.DOTALL)
                hint = hint_match.group(1).strip() if hint_match else "Think about the key concepts."
                
                questions.append({
                    "type": "short_answer",
                    "question": question_text,
                    "expected_answer": answer,
                    "hint": hint,
                    "subject": subject,
                    "difficulty": difficulty
                })
            
            except Exception as e:
                self.logger.warning(f"Failed to parse short answer: {e}")
                continue
        
        if not questions:
            questions.append(self._create_fallback_short_answer(subject, difficulty))
        
        return questions
    
    def _parse_fill_blank_response(
        self,
        response: str,
        subject: str,
        difficulty: str
    ) -> List[Dict[str, Any]]:
        """Parse fill-in-the-blank response"""
        questions = []
        parts = response.split("---")
        
        for part in parts:
            part = part.strip()
            if not part or len(part) < 20:
                continue
            
            try:
                # Extract question
                q_match = re.search(r'Q:\s*(.+?)(?=Answer:|Hint:)', part, re.DOTALL)
                if not q_match:
                    continue
                
                question_text = q_match.group(1).strip()
                
                # Ensure it has a blank
                if "_" not in question_text:
                    continue
                
                # Extract answer
                ans_match = re.search(r'Answer:\s*(.+?)(?=Hint:|$)', part, re.DOTALL)
                answer = ans_match.group(1).strip() if ans_match else "answer"
                
                # Extract hint
                hint_match = re.search(r'Hint:\s*(.+?)(?=---|$)', part, re.DOTALL)
                hint = hint_match.group(1).strip() if hint_match else "Think about the context."
                
                questions.append({
                    "type": "fill_blank",
                    "question": question_text,
                    "correct_answer": answer,
                    "hint": hint,
                    "subject": subject,
                    "difficulty": difficulty
                })
            
            except Exception as e:
                self.logger.warning(f"Failed to parse fill-in-the-blank: {e}")
                continue
        
        if not questions:
            questions.append(self._create_fallback_fill_blank(subject, difficulty))
        
        return questions
    
    def _create_fallback_mcq(self, subject: str, difficulty: str) -> Dict[str, Any]:
        """Create a fallback MCQ if parsing fails"""
        return {
            "type": "mcq",
            "question": f"What is an important concept in {subject}?",
            "options": {
                "A": "Understanding the basics",
                "B": "Memorizing facts",
                "C": "Skipping practice",
                "D": "Ignoring examples"
            },
            "correct_answer": "A",
            "hint": "Think about what helps you learn best.",
            "subject": subject,
            "difficulty": difficulty
        }
    
    def _create_fallback_short_answer(self, subject: str, difficulty: str) -> Dict[str, Any]:
        """Create a fallback short answer question"""
        return {
            "type": "short_answer",
            "question": f"Explain one key concept you learned about {subject}.",
            "expected_answer": "A clear explanation of a key concept with examples.",
            "hint": "Think about the main ideas covered in the material.",
            "subject": subject,
            "difficulty": difficulty
        }
    
    def _create_fallback_fill_blank(self, subject: str, difficulty: str) -> Dict[str, Any]:
        """Create a fallback fill-in-the-blank question"""
        return {
            "type": "fill_blank",
            "question": f"The study of _____ helps us understand {subject} better.",
            "correct_answer": "concepts",
            "hint": "Think about what you're learning.",
            "subject": subject,
            "difficulty": difficulty
        }


# Global question generator agent instance
question_generator_agent = QuestionGeneratorAgent()

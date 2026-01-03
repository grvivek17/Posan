"""
Exam Analysis Agent - Auto-Grading and Feedback Generation

Responsibilities:
- Analyze student answers to questions
- Grade MCQ, short answer, and fill-in-the-blank responses
- Provide detailed feedback and explanations
- Identify knowledge gaps
- Generate personalized recommendations
- Calculate scores and performance metrics
"""

from typing import Dict, Any, List, Optional
import logging
import re
from difflib import SequenceMatcher

from app.agents import AgentBase
from app.services.ai_content import AIContentGenerator

logger = logging.getLogger(__name__)


class ExamAnalysisAgent(AgentBase):
    """
    Agent for analyzing and grading student exam responses.
    
    Features:
    - Auto-grade MCQ questions
    - Evaluate short answer responses with AI
    - Grade fill-in-the-blank answers
    - Provide detailed feedback
    - Identify knowledge gaps
    - Generate improvement recommendations
    """
    
    def __init__(self):
        super().__init__(name="exam_analysis", max_retries=2)
        self.ai_generator = AIContentGenerator()
    
    def _execute_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute exam analysis task.
        
        Input:
            - operation: "grade_exam" or "analyze_performance"
            - questions: List of question objects with student answers
            - student_id: Student ID (optional)
            - exam_id: Exam ID (optional)
            
        Output:
            - graded_questions: Questions with scores and feedback
            - total_score: Total points earned
            - max_score: Maximum possible points
            - percentage: Score percentage
            - feedback: Overall feedback
            - knowledge_gaps: Identified weak areas
            - recommendations: Personalized study recommendations
        """
        operation = input_data.get("operation", "grade_exam")
        
        if operation == "grade_exam":
            return self._grade_exam(input_data)
        elif operation == "analyze_performance":
            return self._analyze_performance(input_data)
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def _grade_exam(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Grade an exam with multiple questions"""
        questions = input_data.get("questions", [])
        student_id = input_data.get("student_id")
        exam_id = input_data.get("exam_id")
        
        if not questions:
            raise ValueError("'questions' list is required")
        
        self.logger.info(f"Grading exam with {len(questions)} questions")
        
        graded_questions = []
        total_score = 0
        max_score = 0
        
        for idx, question in enumerate(questions, 1):
            graded = self._grade_question(question, idx)
            graded_questions.append(graded)
            
            total_score += graded.get("score", 0)
            max_score += graded.get("max_score", 1)
        
        percentage = (total_score / max_score * 100) if max_score > 0 else 0
        
        # Analyze performance
        knowledge_gaps = self._identify_knowledge_gaps(graded_questions)
        recommendations = self._generate_recommendations(graded_questions, percentage)
        overall_feedback = self._generate_overall_feedback(percentage, knowledge_gaps)
        
        return {
            "graded_questions": graded_questions,
            "total_score": total_score,
            "max_score": max_score,
            "percentage": round(percentage, 2),
            "grade": self._calculate_letter_grade(percentage),
            "feedback": overall_feedback,
            "knowledge_gaps": knowledge_gaps,
            "recommendations": recommendations,
            "metadata": {
                "student_id": student_id,
                "exam_id": exam_id,
                "question_count": len(questions),
                "correct_count": sum(1 for q in graded_questions if q.get("is_correct", False))
            }
        }
    
    def _grade_question(self, question: Dict[str, Any], question_num: int) -> Dict[str, Any]:
        """Grade a single question"""
        q_type = question.get("type", "mcq")
        student_answer = question.get("student_answer", "")
        
        if q_type == "mcq":
            return self._grade_mcq(question, question_num)
        elif q_type == "short_answer":
            return self._grade_short_answer(question, question_num)
        elif q_type == "fill_blank":
            return self._grade_fill_blank(question, question_num)
        else:
            return {
                **question,
                "question_number": question_num,
                "score": 0,
                "max_score": 1,
                "is_correct": False,
                "feedback": "Unknown question type"
            }
    
    def _grade_mcq(self, question: Dict[str, Any], question_num: int) -> Dict[str, Any]:
        """Grade a multiple choice question"""
        student_answer = str(question.get("student_answer", "")).strip().upper()
        correct_answer = str(question.get("correct_answer", "")).strip().upper()
        
        is_correct = student_answer == correct_answer
        score = 1 if is_correct else 0
        
        # Generate feedback
        if is_correct:
            feedback = "✓ Correct! Great job!"
        else:
            feedback = f"✗ Incorrect. The correct answer is {correct_answer}."
            
            # Add explanation if available
            if question.get("hint"):
                feedback += f" Hint: {question['hint']}"
        
        return {
            **question,
            "question_number": question_num,
            "score": score,
            "max_score": 1,
            "is_correct": is_correct,
            "feedback": feedback
        }
    
    def _grade_fill_blank(self, question: Dict[str, Any], question_num: int) -> Dict[str, Any]:
        """Grade a fill-in-the-blank question"""
        student_answer = str(question.get("student_answer", "")).strip().lower()
        correct_answer = str(question.get("correct_answer", "")).strip().lower()
        
        # Calculate similarity
        similarity = SequenceMatcher(None, student_answer, correct_answer).ratio()
        
        # Accept answer if similarity > 0.8 or exact match
        is_correct = similarity > 0.8
        score = 1 if is_correct else 0
        
        # Partial credit for close answers
        if not is_correct and similarity > 0.6:
            score = 0.5
            feedback = f"⚠ Partially correct. You wrote '{student_answer}', but the answer is '{correct_answer}'."
        elif is_correct:
            feedback = "✓ Correct!"
        else:
            feedback = f"✗ Incorrect. The correct answer is '{correct_answer}'."
            
            if question.get("hint"):
                feedback += f" Hint: {question['hint']}"
        
        return {
            **question,
            "question_number": question_num,
            "score": score,
            "max_score": 1,
            "is_correct": is_correct,
            "similarity": round(similarity, 2),
            "feedback": feedback
        }
    
    def _grade_short_answer(self, question: Dict[str, Any], question_num: int) -> Dict[str, Any]:
        """Grade a short answer question using AI"""
        student_answer = question.get("student_answer", "").strip()
        expected_answer = question.get("expected_answer", "")
        question_text = question.get("question", "")
        
        if not student_answer:
            return {
                **question,
                "question_number": question_num,
                "score": 0,
                "max_score": 1,
                "is_correct": False,
                "feedback": "No answer provided."
            }
        
        # Use AI to evaluate the answer
        prompt = f"""Evaluate this student's answer to a question.

Question: {question_text}

Expected Answer: {expected_answer}

Student's Answer: {student_answer}

Evaluate the student's answer and provide:
1. Score (0.0 to 1.0): How well does it match the expected answer?
2. Feedback: Brief explanation of what's correct/incorrect
3. Is it correct? (yes/no)

Format:
Score: [0.0-1.0]
Correct: [yes/no]
Feedback: [your feedback]"""
        
        try:
            response = self.ai_generator._generate_text(prompt, max_tokens=200)
            
            # Parse AI response
            score_match = re.search(r'Score:\s*([\d.]+)', response)
            correct_match = re.search(r'Correct:\s*(yes|no)', response, re.IGNORECASE)
            feedback_match = re.search(r'Feedback:\s*(.+?)(?=\n\n|$)', response, re.DOTALL)
            
            score = float(score_match.group(1)) if score_match else 0.5
            is_correct = correct_match.group(1).lower() == 'yes' if correct_match else score > 0.7
            feedback = feedback_match.group(1).strip() if feedback_match else "Answer evaluated."
            
            # Ensure score is in valid range
            score = max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.warning(f"AI grading failed, using fallback: {e}")
            # Fallback: simple similarity check
            similarity = SequenceMatcher(None, student_answer.lower(), expected_answer.lower()).ratio()
            score = similarity
            is_correct = similarity > 0.6
            feedback = f"Your answer has {int(similarity * 100)}% similarity to the expected answer."
        
        return {
            **question,
            "question_number": question_num,
            "score": round(score, 2),
            "max_score": 1,
            "is_correct": is_correct,
            "feedback": feedback
        }
    
    def _identify_knowledge_gaps(self, graded_questions: List[Dict[str, Any]]) -> List[str]:
        """Identify topics where student needs improvement"""
        gaps = []
        
        # Group by topic/subject
        topic_performance = {}
        
        for q in graded_questions:
            topic = q.get("topic") or q.get("subject", "General")
            
            if topic not in topic_performance:
                topic_performance[topic] = {"correct": 0, "total": 0}
            
            topic_performance[topic]["total"] += 1
            if q.get("is_correct", False):
                topic_performance[topic]["correct"] += 1
        
        # Identify weak topics (< 60% correct)
        for topic, perf in topic_performance.items():
            percentage = (perf["correct"] / perf["total"] * 100) if perf["total"] > 0 else 0
            if percentage < 60:
                gaps.append({
                    "topic": topic,
                    "percentage": round(percentage, 2),
                    "questions_attempted": perf["total"],
                    "questions_correct": perf["correct"]
                })
        
        return gaps
    
    def _generate_recommendations(
        self,
        graded_questions: List[Dict[str, Any]],
        percentage: float
    ) -> List[str]:
        """Generate personalized study recommendations"""
        recommendations = []
        
        # Overall performance recommendations
        if percentage >= 90:
            recommendations.append("Excellent work! You've mastered this material.")
            recommendations.append("Challenge yourself with harder problems to continue growing.")
        elif percentage >= 70:
            recommendations.append("Good job! You understand most of the concepts.")
            recommendations.append("Review the questions you missed to fill in knowledge gaps.")
        elif percentage >= 50:
            recommendations.append("You're making progress, but need more practice.")
            recommendations.append("Focus on understanding the core concepts better.")
        else:
            recommendations.append("This material needs more attention.")
            recommendations.append("Consider reviewing the study material and trying practice questions.")
        
        # Topic-specific recommendations
        incorrect_questions = [q for q in graded_questions if not q.get("is_correct", False)]
        
        if incorrect_questions:
            topics = list(set(q.get("topic") or q.get("subject", "this topic") for q in incorrect_questions))
            if topics:
                recommendations.append(f"Focus on: {', '.join(topics[:3])}")
        
        return recommendations
    
    def _generate_overall_feedback(
        self,
        percentage: float,
        knowledge_gaps: List[Dict[str, Any]]
    ) -> str:
        """Generate overall performance feedback"""
        if percentage >= 90:
            feedback = "Outstanding performance! You've demonstrated excellent understanding of the material."
        elif percentage >= 80:
            feedback = "Great work! You have a strong grasp of most concepts."
        elif percentage >= 70:
            feedback = "Good effort! You understand the basics well."
        elif percentage >= 60:
            feedback = "Fair performance. With more practice, you can improve significantly."
        elif percentage >= 50:
            feedback = "You're on the right track, but need more study time."
        else:
            feedback = "This material requires more attention. Don't get discouraged - practice makes perfect!"
        
        if knowledge_gaps:
            gap_topics = [gap["topic"] for gap in knowledge_gaps[:2]]
            feedback += f" Pay special attention to: {', '.join(gap_topics)}."
        
        return feedback
    
    def _calculate_letter_grade(self, percentage: float) -> str:
        """Convert percentage to letter grade"""
        if percentage >= 90:
            return "A"
        elif percentage >= 80:
            return "B"
        elif percentage >= 70:
            return "C"
        elif percentage >= 60:
            return "D"
        else:
            return "F"
    
    def _analyze_performance(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze performance trends over multiple exams"""
        # This would analyze historical data
        # For now, return a placeholder
        return {
            "message": "Performance analysis across multiple exams",
            "note": "This feature requires historical exam data"
        }


# Global exam analysis agent instance
exam_analysis_agent = ExamAnalysisAgent()

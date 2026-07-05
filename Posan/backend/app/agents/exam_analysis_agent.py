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
from app.services.ai_content import ContentGenerator

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
        self.ai_generator = ContentGenerator()
    
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
        """Analyze performance trends over multiple exams using real historical data."""
        exams = input_data.get("exams", [])
        answers = input_data.get("answers", [])

        if not exams:
            return {
                "summary": {
                    "total_exams": 0,
                    "average_score": 0,
                    "overall_trend": "no_data",
                    "message": "No exam history found. Complete some practice exams to see your performance analysis."
                },
                "by_subject": {},
                "by_question_type": {},
                "knowledge_gaps": {"recurring": [], "improving": [], "critical": []},
                "recommendations": ["Start with a practice exam to build your performance history."],
                "score_timeline": []
            }

        # --- Score timeline (chronological) ---
        sorted_exams = sorted(exams, key=lambda e: e.get("created_at", ""))
        score_timeline = [
            {
                "date": e.get("created_at", ""),
                "percentage": e.get("percentage", 0),
                "subject": e.get("subject", "General"),
                "grade": e.get("letter_grade", "")
            }
            for e in sorted_exams if e.get("percentage") is not None
        ]

        scores = [e.get("percentage", 0) for e in sorted_exams if e.get("percentage") is not None]
        avg_score = sum(scores) / len(scores) if scores else 0
        highest = max(scores) if scores else 0
        lowest = min(scores) if scores else 0

        # --- Overall trend ---
        if len(scores) >= 3:
            first_half = scores[:len(scores)//2]
            second_half = scores[len(scores)//2:]
            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)
            diff = second_avg - first_avg
            if diff > 5:
                overall_trend = "improving"
            elif diff < -5:
                overall_trend = "declining"
            else:
                overall_trend = "stable"
        elif len(scores) == 2:
            overall_trend = "improving" if scores[1] > scores[0] else ("declining" if scores[1] < scores[0] else "stable")
        else:
            overall_trend = "just_started"

        # --- Consistency (coefficient of variation) ---
        if len(scores) >= 2:
            mean = avg_score
            variance = sum((s - mean) ** 2 for s in scores) / len(scores)
            std_dev = variance ** 0.5
            consistency = max(0, round(1 - (std_dev / 100), 2))
        else:
            consistency = 1.0

        # --- By subject analysis ---
        subject_data = {}
        for e in sorted_exams:
            subj = e.get("subject") or "General"
            if subj not in subject_data:
                subject_data[subj] = []
            if e.get("percentage") is not None:
                subject_data[subj].append(e["percentage"])

        by_subject = {}
        for subj, subj_scores in subject_data.items():
            subj_avg = sum(subj_scores) / len(subj_scores)
            if len(subj_scores) >= 2:
                subj_trend = "improving" if subj_scores[-1] > subj_scores[0] + 5 else (
                    "declining" if subj_scores[-1] < subj_scores[0] - 5 else "stable"
                )
            else:
                subj_trend = "just_started"
            by_subject[subj] = {
                "exams": len(subj_scores),
                "average": round(subj_avg, 1),
                "trend": subj_trend,
                "latest_score": subj_scores[-1] if subj_scores else 0,
                "best_score": max(subj_scores) if subj_scores else 0
            }

        strongest = max(by_subject.items(), key=lambda x: x[1]["average"])[0] if by_subject else None
        weakest = min(by_subject.items(), key=lambda x: x[1]["average"])[0] if by_subject else None

        # --- By question type analysis ---
        type_stats = {}
        for a in answers:
            q_type = a.get("question_type", "unknown")
            if q_type not in type_stats:
                type_stats[q_type] = {"correct": 0, "total": 0}
            type_stats[q_type]["total"] += 1
            if a.get("is_correct"):
                type_stats[q_type]["correct"] += 1

        by_question_type = {}
        for q_type, data in type_stats.items():
            rate = (data["correct"] / data["total"]) if data["total"] > 0 else 0
            by_question_type[q_type] = {
                "success_rate": round(rate, 2),
                "total_attempted": data["total"],
                "correct": data["correct"]
            }

        # --- Knowledge gap analysis ---
        gap_frequency = {}
        for e in sorted_exams:
            gaps = e.get("knowledge_gaps_json") or []
            if isinstance(gaps, list):
                for gap in gaps:
                    topic = gap.get("topic", "") if isinstance(gap, dict) else str(gap)
                    if topic:
                        if topic not in gap_frequency:
                            gap_frequency[topic] = {"appearances": 0, "first_seen": e.get("created_at", ""), "last_seen": ""}
                        gap_frequency[topic]["appearances"] += 1
                        gap_frequency[topic]["last_seen"] = e.get("created_at", "")

        recurring = [t for t, d in gap_frequency.items() if d["appearances"] >= 2]
        recent_gaps = [t for t, d in gap_frequency.items() if d["last_seen"] == sorted_exams[-1].get("created_at", "")] if sorted_exams else []
        older_gaps = [t for t in gap_frequency if t not in recent_gaps]
        improving = [t for t in older_gaps if gap_frequency[t]["appearances"] >= 2]
        critical = [t for t in recurring if t in recent_gaps]

        # --- Recommendations ---
        recommendations = []
        if overall_trend == "improving":
            recommendations.append("Great progress! Your scores are trending upward.")
        elif overall_trend == "declining":
            recommendations.append("Your recent scores have dipped. Consider reviewing fundamentals.")
        elif overall_trend == "stable":
            recommendations.append("Your performance is consistent. Try challenging yourself with harder material.")

        if weakest and strongest and weakest != strongest:
            recommendations.append(f"Your strongest subject is {strongest}. Focus more on {weakest} to balance out.")

        if critical:
            recommendations.append(f"Critical areas to review: {', '.join(critical[:3])}")
        elif recurring:
            recommendations.append(f"Recurring weak areas: {', '.join(recurring[:3])}. Extra practice recommended.")

        best_type = max(by_question_type.items(), key=lambda x: x[1]["success_rate"])[0] if by_question_type else None
        worst_type = min(by_question_type.items(), key=lambda x: x[1]["success_rate"])[0] if by_question_type else None
        if best_type and worst_type and best_type != worst_type:
            recommendations.append(f"You excel at {best_type} questions. Practice more {worst_type} questions.")

        if avg_score >= 80:
            recommendations.append("Excellent overall performance! Consider advancing to harder material.")
        elif avg_score >= 60:
            recommendations.append("Good work! Regular practice will push you to the next level.")
        else:
            recommendations.append("Keep practicing! Review study materials and try the questions again.")

        return {
            "summary": {
                "total_exams": len(exams),
                "average_score": round(avg_score, 1),
                "highest_score": round(highest, 1),
                "lowest_score": round(lowest, 1),
                "overall_trend": overall_trend,
                "consistency": consistency
            },
            "by_subject": by_subject,
            "by_question_type": by_question_type,
            "knowledge_gaps": {
                "recurring": recurring[:5],
                "improving": improving[:5],
                "critical": critical[:5]
            },
            "recommendations": recommendations,
            "score_timeline": score_timeline,
            "strongest_subject": strongest,
            "weakest_subject": weakest
        }


# Global exam analysis agent instance
exam_analysis_agent = ExamAnalysisAgent()

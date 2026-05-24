"""
Database models for Exam/Test Paper Persistence

New tables:
- exams: Exam/test sessions with scores and feedback
- exam_answers: Individual graded answers per exam
- assignments: Homework assignments tracking
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


def generate_uuid():
    """Generate UUID as string"""
    return str(uuid.uuid4())


class Exam(Base):
    """Exam/test sessions with scores and feedback"""
    __tablename__ = "exams"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False)
    title = Column(String)
    subject = Column(String)
    grade = Column(Integer)
    total_score = Column(Float)
    max_score = Column(Float)
    percentage = Column(Float)
    letter_grade = Column(String)
    performance_level = Column(String)
    feedback = Column(Text)
    recommendations = Column(Text)
    knowledge_gaps_json = Column(JSON)
    source_type = Column(String)  # 'practice', 'upload', 'manual'
    source_material_id = Column(String, nullable=True)  # FK to materials if from practice
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    answers = relationship("ExamAnswer", back_populates="exam", cascade="all, delete-orphan")


class ExamAnswer(Base):
    """Individual graded answers per exam"""
    __tablename__ = "exam_answers"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    exam_id = Column(String, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    question_number = Column(Integer)
    question_type = Column(String)  # 'mcq', 'short_answer', 'fill_blank'
    question_text = Column(Text)
    student_answer = Column(Text)
    correct_answer = Column(Text)
    score = Column(Float)
    max_score = Column(Float)
    is_correct = Column(Boolean)
    feedback = Column(Text)
    similarity = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    exam = relationship("Exam", back_populates="answers")


class Assignment(Base):
    """Homework assignments tracking"""
    __tablename__ = "assignments"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False)
    title = Column(String, nullable=False)
    subject = Column(String)
    description = Column(Text)
    due_date = Column(DateTime)
    status = Column(String, default="pending")  # 'pending', 'in_progress', 'completed'
    file_url = Column(String, nullable=True)
    file_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

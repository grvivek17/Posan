"""
Database models for Multi-Agent Homework System

New tables:
- materials: Study materials uploaded by users
- material_chunks: Text chunks with metadata
- agent_runs: Agent execution logs (for traceability)
"""

from sqlalchemy import Column, String, Integer, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base


def generate_uuid():
    """Generate UUID as string"""
    return str(uuid.uuid4())


class Material(Base):
    """Study materials uploaded by users"""
    __tablename__ = "materials"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    user_id = Column(String, nullable=False)  # Removed FK to avoid circular dependency
    title = Column(String, nullable=False)
    subject = Column(String)
    topic = Column(String)
    grade = Column(Integer)
    storage_url = Column(String, nullable=False)  # Path to original file
    file_extension = Column(String, nullable=False)
    is_ocr = Column(Boolean, default=False)
    total_chunks = Column(Integer, default=0)
    total_tokens = Column(Integer, default=0)
    topics_json = Column(JSON)  # Extracted topics
    metadata_json = Column(JSON)  # Additional metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    chunks = relationship("MaterialChunk", back_populates="material", cascade="all, delete-orphan")


class MaterialChunk(Base):
    """Text chunks from study materials"""
    __tablename__ = "material_chunks"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    material_id = Column(String, ForeignKey("materials.id", ondelete="CASCADE"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    tokens = Column(Integer, nullable=False)
    heading = Column(String)
    topic = Column(String)
    embedding_vector = Column(JSON)  # Store as JSON array (will use FAISS separately)
    metadata_json = Column(JSON)  # Section info, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    material = relationship("Material", back_populates="chunks")


class AgentRunLog(Base):
    """Agent execution logs for traceability"""
    __tablename__ = "agent_runs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    agent_name = Column(String, nullable=False, index=True)
    task_id = Column(String, nullable=False, unique=True, index=True)
    input_json = Column(JSON, nullable=False)
    output_json = Column(JSON)
    status = Column(String, nullable=False)  # success, failure, partial
    error = Column(Text)
    user_id = Column(String)  # Removed FK to avoid circular dependency
    related_entity = Column(String)  # materials, exams, etc.
    related_id = Column(String)
    execution_time_ms = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)

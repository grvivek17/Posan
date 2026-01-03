"""
Database service for Materials and Chunks

Handles CRUD operations for:
- Materials
- Material Chunks
- Agent Run Logs
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from datetime import datetime

from app.models.homework_agents import Material, MaterialChunk, AgentRunLog
from app.agents import AgentRun


class MaterialService:
    """Service for managing study materials and chunks"""
    
    @staticmethod
    def create_material(
        db: Session,
        user_id: str,
        title: str,
        storage_url: str,
        file_extension: str,
        subject: Optional[str] = None,
        topic: Optional[str] = None,
        grade: Optional[int] = None,
        is_ocr: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Material:
        """
        Create a new material record.
        
        Args:
            db: Database session
            user_id: User ID
            title: Material title
            storage_url: Path to stored file
            file_extension: File extension
            subject: Subject (optional)
            topic: Topic (optional)
            grade: Grade level (optional)
            is_ocr: Whether OCR was used
            metadata: Additional metadata
            
        Returns:
            Created Material instance
        """
        material = Material(
            user_id=user_id,
            title=title,
            subject=subject,
            topic=topic,
            grade=grade,
            storage_url=storage_url,
            file_extension=file_extension,
            is_ocr=is_ocr,
            metadata_json=metadata or {}
        )
        
        db.add(material)
        db.commit()
        db.refresh(material)
        
        return material
    
    @staticmethod
    def add_chunks(
        db: Session,
        material_id: str,
        chunks: List[Dict[str, Any]]
    ) -> List[MaterialChunk]:
        """
        Add chunks to a material.
        
        Args:
            db: Database session
            material_id: Material ID
            chunks: List of chunk dictionaries
            
        Returns:
            List of created MaterialChunk instances
        """
        chunk_objects = []
        
        for chunk_data in chunks:
            chunk = MaterialChunk(
                material_id=material_id,
                chunk_index=chunk_data.get("chunk_index", 0),
                text=chunk_data["text"],
                tokens=chunk_data["tokens"],
                heading=chunk_data.get("heading"),
                topic=chunk_data.get("topic"),
                metadata_json=chunk_data.get("metadata", {})
            )
            chunk_objects.append(chunk)
        
        db.add_all(chunk_objects)
        
        # Update material stats
        material = db.query(Material).filter(Material.id == material_id).first()
        if material:
            material.total_chunks = len(chunk_objects)
            material.total_tokens = sum(c.tokens for c in chunk_objects)
            
            # Extract unique topics
            topics = list(set(c.topic for c in chunk_objects if c.topic))
            material.topics_json = topics
        
        db.commit()
        
        for chunk in chunk_objects:
            db.refresh(chunk)
        
        return chunk_objects
    
    @staticmethod
    def get_material(db: Session, material_id: str) -> Optional[Material]:
        """Get material by ID"""
        return db.query(Material).filter(Material.id == material_id).first()
    
    @staticmethod
    def get_user_materials(
        db: Session,
        user_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Material]:
        """Get materials for a user"""
        return db.query(Material)\
            .filter(Material.user_id == user_id)\
            .order_by(Material.created_at.desc())\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def get_material_chunks(
        db: Session,
        material_id: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[MaterialChunk]:
        """Get chunks for a material"""
        return db.query(MaterialChunk)\
            .filter(MaterialChunk.material_id == material_id)\
            .order_by(MaterialChunk.chunk_index)\
            .offset(skip)\
            .limit(limit)\
            .all()
    
    @staticmethod
    def search_chunks_by_topic(
        db: Session,
        topic: str,
        user_id: Optional[str] = None,
        limit: int = 10
    ) -> List[MaterialChunk]:
        """
        Search chunks by topic.
        
        Args:
            db: Database session
            topic: Topic to search for
            user_id: Optional user ID filter
            limit: Maximum results
            
        Returns:
            List of matching chunks
        """
        query = db.query(MaterialChunk)\
            .filter(MaterialChunk.topic.ilike(f"%{topic}%"))
        
        if user_id:
            query = query.join(Material).filter(Material.user_id == user_id)
        
        return query.limit(limit).all()
    
    @staticmethod
    def delete_material(db: Session, material_id: str) -> bool:
        """
        Delete a material and all its chunks.
        
        Args:
            db: Database session
            material_id: Material ID
            
        Returns:
            True if deleted, False if not found
        """
        material = db.query(Material).filter(Material.id == material_id).first()
        
        if not material:
            return False
        
        db.delete(material)
        db.commit()
        
        return True


class AgentLogService:
    """Service for managing agent execution logs"""
    
    @staticmethod
    def log_agent_run(
        db: Session,
        agent_run: AgentRun
    ) -> AgentRunLog:
        """
        Save an agent run to the database.
        
        Args:
            db: Database session
            agent_run: AgentRun instance from agent execution
            
        Returns:
            Created AgentRunLog instance
        """
        log = AgentRunLog(
            agent_name=agent_run.agent_name,
            task_id=agent_run.task_id,
            input_json=agent_run.input_json,
            output_json=agent_run.output_json,
            status=agent_run.status,
            error=agent_run.error,
            user_id=agent_run.user_id,
            related_entity=agent_run.related_entity,
            related_id=agent_run.related_id,
            execution_time_ms=agent_run.execution_time_ms,
            created_at=agent_run.created_at
        )
        
        db.add(log)
        db.commit()
        db.refresh(log)
        
        return log
    
    @staticmethod
    def get_agent_runs(
        db: Session,
        agent_name: Optional[str] = None,
        user_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[AgentRunLog]:
        """
        Get agent runs with optional filters.
        
        Args:
            db: Database session
            agent_name: Filter by agent name
            user_id: Filter by user ID
            status: Filter by status
            limit: Maximum results
            
        Returns:
            List of agent run logs
        """
        query = db.query(AgentRunLog)
        
        if agent_name:
            query = query.filter(AgentRunLog.agent_name == agent_name)
        
        if user_id:
            query = query.filter(AgentRunLog.user_id == user_id)
        
        if status:
            query = query.filter(AgentRunLog.status == status)
        
        return query.order_by(AgentRunLog.created_at.desc()).limit(limit).all()
    
    @staticmethod
    def get_run_by_task_id(db: Session, task_id: str) -> Optional[AgentRunLog]:
        """Get agent run by task ID"""
        return db.query(AgentRunLog).filter(AgentRunLog.task_id == task_id).first()


# Global service instances
material_service = MaterialService()
agent_log_service = AgentLogService()

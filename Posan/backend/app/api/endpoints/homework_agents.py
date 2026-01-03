"""
Agent-based Homework API Endpoints

New endpoints that use the multi-agent architecture while maintaining
backward compatibility with existing homework features.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import tempfile
import os
from pathlib import Path

from app.agents.ingestion_agent import ingestion_agent
from app.agents import coordinator

router = APIRouter()


# ============= REQUEST/RESPONSE SCHEMAS =============

class MaterialUploadResponse(BaseModel):
    """Response for material upload"""
    success: bool
    material_id: str
    task_id: str
    chunks_created: int
    total_tokens: int
    topics: List[str]
    processing_time_ms: float
    metadata: Dict[str, Any]


class AgentStatusResponse(BaseModel):
    """Response for agent status check"""
    agent_name: str
    total_runs: int
    recent_runs: List[Dict[str, Any]]


# ============= MATERIAL INGESTION ENDPOINTS =============

@router.post("/materials/upload-v2", response_model=MaterialUploadResponse)
async def upload_material_v2(
    file: UploadFile = File(..., description="Study material (PDF or image)"),
    subject: Optional[str] = Form(None, description="Subject (Math, Science, etc.)"),
    topic: Optional[str] = Form(None, description="Specific topic"),
    grade: Optional[int] = Form(None, description="Grade level (1-8)"),
    user_id: str = Form(..., description="User ID")
):
    """
    Upload and process study material using the new agent architecture.
    
    This endpoint:
    1. Saves the uploaded file
    2. Uses the Ingestion Agent to extract and chunk text
    3. Detects document structure and topics
    4. Returns processed chunks ready for embedding
    
    **New Features vs /study-material/upload:**
    - Intelligent chunking with section awareness
    - Topic extraction
    - Structure detection
    - Better metadata
    - Agent-based processing with logging
    """
    # Validate file type
    allowed_extensions = ['.pdf', '.jpg', '.jpeg', '.png']
    file_extension = Path(file.filename).suffix.lower()
    
    if file_extension not in allowed_extensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type. Allowed: {', '.join(allowed_extensions)}"
        )
    
    # Validate file size (max 10MB)
    max_size = 10 * 1024 * 1024
    
    temp_file_path = None
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            if len(content) > max_size:
                raise HTTPException(status_code=400, detail="File too large (max 10MB)")
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Generate material ID
        import uuid
        material_id = str(uuid.uuid4())
        
        # Execute ingestion agent
        output = ingestion_agent.execute(
            input_data={
                "file_path": temp_file_path,
                "file_extension": file_extension,
                "material_id": material_id,
                "subject": subject,
                "grade": grade
            },
            user_id=user_id,
            related_entity="materials",
            related_id=material_id
        )
        
        # Check for failure
        if output.status != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Ingestion failed: {output.error}"
            )
        
        result = output.result
        
        return MaterialUploadResponse(
            success=True,
            material_id=material_id,
            task_id=output.task_id,
            chunks_created=result["total_chunks"],
            total_tokens=result["total_tokens"],
            topics=result["topics"],
            processing_time_ms=output.execution_time_ms,
            metadata=result["metadata"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
    finally:
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                print(f"Warning: Could not delete temp file: {e}")


@router.get("/materials/{material_id}/chunks")
async def get_material_chunks(
    material_id: str,
    limit: int = Query(default=10, ge=1, le=100, description="Number of chunks to return")
):
    """
    Get chunks for a specific material.
    
    This is a placeholder - in production, chunks would be stored in a database.
    For now, it demonstrates the structure of chunk data.
    """
    # TODO: Implement database storage and retrieval
    return {
        "material_id": material_id,
        "message": "Chunk storage not yet implemented. Chunks are currently returned in the upload response.",
        "note": "Next phase will add vector database integration for chunk storage and retrieval."
    }


# ============= AGENT STATUS ENDPOINTS =============

@router.get("/agents/status/{agent_name}", response_model=AgentStatusResponse)
async def get_agent_status(
    agent_name: str,
    limit: int = Query(default=10, ge=1, le=100, description="Number of recent runs to return")
):
    """
    Get status and recent runs for a specific agent.
    
    Available agents:
    - ingestion: Material processing and chunking
    - retrieval: Vector search (coming soon)
    - question_generator: Practice question generation (coming soon)
    - exam_analysis: Exam grading (coming soon)
    - planner: Study plan generation (coming soon)
    - safety: Content filtering (coming soon)
    """
    # Get agent from coordinator
    agent = coordinator.get_agent(agent_name)
    
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found")
    
    # Get recent runs
    recent_runs = agent.get_runs(limit=limit)
    
    return AgentStatusResponse(
        agent_name=agent_name,
        total_runs=len(agent.runs),
        recent_runs=[
            {
                "task_id": run.task_id,
                "status": run.status,
                "execution_time_ms": run.execution_time_ms,
                "created_at": run.created_at.isoformat(),
                "has_error": run.error is not None
            }
            for run in recent_runs
        ]
    )


@router.get("/agents/list")
async def list_agents():
    """
    List all registered agents and their status.
    """
    agents_info = []
    
    for agent_name, agent in coordinator.agents.items():
        agents_info.append({
            "name": agent_name,
            "total_runs": len(agent.runs),
            "max_retries": agent.max_retries,
            "status": "active"
        })
    
    return {
        "total_agents": len(coordinator.agents),
        "agents": agents_info
    }


# ============= WORKFLOW ENDPOINTS (DEMO) =============

@router.post("/workflows/demo/material-to-practice")
async def demo_material_to_practice_workflow(
    file: UploadFile = File(...),
    subject: str = Form(...),
    grade: int = Form(...),
    user_id: str = Form(...)
):
    """
    Demo workflow: Upload material → Process → Generate practice questions
    
    This demonstrates how multiple agents work together in a workflow.
    Currently only shows the ingestion step; question generation will be added next.
    """
    # Save file temporarily
    file_extension = Path(file.filename).suffix.lower()
    
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name
    
    try:
        import uuid
        material_id = str(uuid.uuid4())
        
        # Define workflow
        workflow = [
            {
                "agent": "ingestion",
                "input": {
                    "file_path": temp_file_path,
                    "file_extension": file_extension,
                    "material_id": material_id,
                    "subject": subject,
                    "grade": grade
                },
                "output_key": "ingestion_result"
            }
            # TODO: Add retrieval and question generation steps
        ]
        
        # Execute workflow
        result = coordinator.execute_workflow(workflow, user_id=user_id)
        
        return {
            "workflow_status": result["status"],
            "material_id": material_id,
            "ingestion": result["results"].get("ingestion_result"),
            "note": "Question generation step coming in next phase"
        }
        
    finally:
        if os.path.exists(temp_file_path):
            os.unlink(temp_file_path)


# Register ingestion agent with coordinator
coordinator.register_agent(ingestion_agent)

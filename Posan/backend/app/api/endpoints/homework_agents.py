"""
Agent-based Homework API Endpoints

New endpoints that use the multi-agent architecture while maintaining
backward compatibility with existing homework features.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query, Depends
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import tempfile
import os
import logging
from pathlib import Path

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.exam import Exam, ExamAnswer, Assignment
from app.agents.ingestion_agent import ingestion_agent
from app.agents.retrieval_agent import retrieval_agent
from app.agents.question_generator_agent import question_generator_agent
from app.agents.exam_analysis_agent import exam_analysis_agent
from app.agents import coordinator
from app.core.database import get_db
from app.core.subscription_deps import require_pro_subscription
from app.services.material_service import material_service, agent_log_service

logger = logging.getLogger(__name__)

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
    user_id: str = Form(..., description="User ID"),
    current_user: User = Depends(require_pro_subscription)  # 🔒 PRO REQUIRED
):
    """
    Upload and process study material using the new agent architecture.
    
    **🌟 PRO FEATURE - Requires Pro or Premium subscription**
    
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
    limit: int = Query(default=10, ge=1, le=100, description="Number of chunks to return"),
    db: Session = Depends(get_db)
):
    """
    Get chunks for a specific material from the database.
    """
    material = material_service.get_material(db, material_id)
    if not material:
        raise HTTPException(status_code=404, detail=f"Material '{material_id}' not found")

    chunks = material_service.get_material_chunks(db, material_id, limit=limit)

    return {
        "material_id": material_id,
        "title": material.title,
        "subject": material.subject,
        "total_chunks": material.total_chunks,
        "chunks": [
            {
                "id": chunk.id,
                "chunk_index": chunk.chunk_index,
                "text": chunk.text,
                "tokens": chunk.tokens,
                "heading": chunk.heading,
                "topic": chunk.topic,
                "metadata": chunk.metadata_json
            }
            for chunk in chunks
        ]
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


# ============= SEMANTIC SEARCH ENDPOINTS (Phase 2) =============

@router.post("/search/create-index")
async def create_search_index(
    index_name: str = Form(..., description="Name for the index"),
    chunks: str = Form(..., description="JSON string of chunks"),
    force_recreate: bool = Form(default=False, description="Force recreate if exists")
):
    """
    Create a FAISS index for semantic search.
    
    This endpoint:
    1. Takes chunks from material processing
    2. Generates embeddings using sentence-transformers
    3. Creates FAISS index for fast similarity search
    4. Saves index to disk for persistence
    
    **Use after material upload to enable semantic search**
    """
    import json
    
    try:
        # Parse chunks JSON
        chunks_list = json.loads(chunks)
        
        # Execute retrieval agent
        output = retrieval_agent.execute(
            input_data={
                "operation": "create_index",
                "index_name": index_name,
                "chunks": chunks_list,
                "force_recreate": force_recreate
            },
            related_entity="indices",
            related_id=index_name
        )
        
        if output.status != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Index creation failed: {output.error}"
            )
        
        return {
            "success": True,
            "task_id": output.task_id,
            "processing_time_ms": output.execution_time_ms,
            **output.result
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating index: {str(e)}")


@router.post("/search/query")
async def semantic_search(
    index_name: str = Form(..., description="Index to search"),
    query: str = Form(..., description="Search query"),
    top_k: int = Form(default=5, description="Number of results"),
    min_score: float = Form(default=0.0, description="Minimum similarity score (0-1)")
):
    """
    Perform semantic search in a material index.
    
    This endpoint:
    1. Takes a natural language query
    2. Generates query embedding
    3. Searches FAISS index for similar chunks
    4. Returns ranked results with similarity scores
    
    **Example queries:**
    - "What is photosynthesis?"
    - "Explain multiplication"
    - "Tell me about the solar system"
    """
    try:
        # Execute retrieval agent
        output = retrieval_agent.execute(
            input_data={
                "operation": "search",
                "index_name": index_name,
                "query": query,
                "top_k": top_k,
                "min_score": min_score
            },
            related_entity="search",
            related_id=index_name
        )
        
        if output.status != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Search failed: {output.error}"
            )
        
        return {
            "success": True,
            "task_id": output.task_id,
            "processing_time_ms": output.execution_time_ms,
            **output.result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error searching: {str(e)}")


@router.post("/search/multi-index")
async def multi_index_search(
    index_names: str = Form(..., description="Comma-separated index names"),
    query: str = Form(..., description="Search query"),
    top_k: int = Form(default=5, description="Number of results"),
    min_score: float = Form(default=0.0, description="Minimum similarity score (0-1)")
):
    """
    Search across multiple material indices.
    
    Useful for:
    - Searching all materials for a user
    - Cross-subject search
    - Finding related content across topics
    """
    try:
        # Parse index names
        indices = [name.strip() for name in index_names.split(",")]
        
        # Execute retrieval agent
        output = retrieval_agent.execute(
            input_data={
                "operation": "search_multi",
                "index_names": indices,
                "query": query,
                "top_k": top_k,
                "min_score": min_score
            },
            related_entity="search",
            related_id="multi"
        )
        
        if output.status != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Multi-index search failed: {output.error}"
            )
        
        return {
            "success": True,
            "task_id": output.task_id,
            "processing_time_ms": output.execution_time_ms,
            **output.result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in multi-index search: {str(e)}")


@router.get("/search/indices")
async def list_search_indices():
    """
    List all available search indices.
    
    Shows:
    - Index names
    - Number of chunks in each index
    - Whether index is loaded in memory
    """
    try:
        # Execute retrieval agent
        output = retrieval_agent.execute(
            input_data={"operation": "list_indices"},
            related_entity="indices",
            related_id="list"
        )
        
        if output.status != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Failed to list indices: {output.error}"
            )
        
        return {
            "success": True,
            **output.result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error listing indices: {str(e)}")


@router.delete("/search/indices/{index_name}")
async def delete_search_index(index_name: str):
    """
    Delete a search index.
    
    This removes both the FAISS index and metadata from disk.
    """
    try:
        # Execute retrieval agent
        output = retrieval_agent.execute(
            input_data={
                "operation": "delete_index",
                "index_name": index_name
            },
            related_entity="indices",
            related_id=index_name
        )
        
        if output.status != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete index: {output.error}"
            )
        
        return {
            "success": True,
            **output.result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting index: {str(e)}")


# ============= QUESTION GENERATION ENDPOINTS (Phase 3) =============

@router.post("/questions/generate")
async def generate_questions(
    context: str = Form(..., description="Text context for question generation"),
    grade: int = Form(..., description="Grade level (1-8)"),
    subject: str = Form(default="General", description="Subject area"),
    question_types: str = Form(default="mcq,short_answer", description="Comma-separated types"),
    count: int = Form(default=5, description="Number of questions"),
    difficulty: str = Form(default="medium", description="Difficulty level"),
    current_user: User = Depends(require_pro_subscription)  # 🔒 PRO REQUIRED
):
    """
    Generate practice questions from text context.
    
    **🌟 PRO FEATURE - Requires Pro or Premium subscription**
    
    **Question Types:**
    - `mcq`: Multiple choice (4 options)
    - `short_answer`: Short answer questions
    - `fill_blank`: Fill in the blank
    
    **Difficulty Levels:**
    - `easy`: Simple, straightforward questions
    - `medium`: Moderate complexity
    - `hard`: Challenging, requires deeper understanding
    
    **Example:**
    ```
    context: "Photosynthesis is the process by which plants make food..."
    grade: 5
    subject: "Science"
    question_types: "mcq,short_answer"
    count: 5
    ```
    """
    try:
        # Parse question types
        types_list = [t.strip() for t in question_types.split(",")]
        
        # Execute question generator agent
        output = question_generator_agent.execute(
            input_data={
                "operation": "generate_questions",
                "context": context,
                "grade": grade,
                "subject": subject,
                "question_types": types_list,
                "count": count,
                "difficulty": difficulty
            },
            related_entity="questions",
            related_id=f"{subject}_{grade}"
        )
        
        if output.status != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Question generation failed: {output.error}"
            )
        
        return {
            "success": True,
            "task_id": output.task_id,
            "processing_time_ms": output.execution_time_ms,
            **output.result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating questions: {str(e)}")


@router.post("/questions/from-material")
async def generate_questions_from_material(
    index_name: str = Form(..., description="Material index to search"),
    topic: str = Form(..., description="Topic or query to find relevant content"),
    grade: int = Form(..., description="Grade level (1-8)"),
    subject: str = Form(default="General", description="Subject area"),
    question_types: str = Form(default="mcq,short_answer", description="Question types"),
    count: int = Form(default=5, description="Number of questions"),
    difficulty: str = Form(default="medium", description="Difficulty level")
):
    """
    Generate questions from a specific material using semantic search.
    
    **Workflow:**
    1. Search material index for relevant chunks
    2. Use top chunks as context
    3. Generate practice questions
    
    **This combines Retrieval Agent + Question Generator!**
    
    **Example:**
    ```
    index_name: "math_grade5"
    topic: "multiplication"
    grade: 5
    count: 10
    ```
    """
    try:
        # Step 1: Search for relevant chunks
        search_output = retrieval_agent.execute(
            input_data={
                "operation": "search",
                "index_name": index_name,
                "query": topic,
                "top_k": 5,
                "min_score": 0.0
            },
            related_entity="search",
            related_id=index_name
        )
        
        if search_output.status != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Search failed: {search_output.error}"
            )
        
        # Extract chunks from search results
        search_results = search_output.result.get("results", [])
        chunks = [result["chunk"] for result in search_results]
        
        if not chunks:
            raise HTTPException(
                status_code=404,
                detail=f"No relevant content found for topic: {topic}"
            )
        
        # Step 2: Generate questions from chunks
        types_list = [t.strip() for t in question_types.split(",")]
        
        question_output = question_generator_agent.execute(
            input_data={
                "operation": "generate_questions",
                "chunks": chunks,
                "grade": grade,
                "subject": subject,
                "question_types": types_list,
                "count": count,
                "difficulty": difficulty
            },
            related_entity="questions",
            related_id=index_name
        )
        
        if question_output.status != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Question generation failed: {question_output.error}"
            )
        
        return {
            "success": True,
            "search_task_id": search_output.task_id,
            "question_task_id": question_output.task_id,
            "chunks_used": len(chunks),
            "processing_time_ms": search_output.execution_time_ms + question_output.execution_time_ms,
            **question_output.result
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/questions/practice-set")
async def create_practice_set(
    title: str = Form(..., description="Practice set title"),
    context: str = Form(..., description="Text context"),
    grade: int = Form(..., description="Grade level (1-8)"),
    subject: str = Form(default="General", description="Subject area"),
    question_types: str = Form(default="mcq,short_answer,fill_blank", description="Question types"),
    count: int = Form(default=10, description="Number of questions"),
    difficulty: str = Form(default="medium", description="Difficulty level")
):
    """
    Create a complete practice set with metadata.
    
    **Returns:**
    - Practice set with title and description
    - All generated questions
    - Metadata (grade, subject, difficulty)
    
    **Perfect for:**
    - Creating homework assignments
    - Quiz generation
    - Practice worksheets
    """
    try:
        types_list = [t.strip() for t in question_types.split(",")]
        
        output = question_generator_agent.execute(
            input_data={
                "operation": "generate_practice_set",
                "title": title,
                "context": context,
                "grade": grade,
                "subject": subject,
                "question_types": types_list,
                "count": count,
                "difficulty": difficulty
            },
            related_entity="practice_sets",
            related_id=f"{subject}_{grade}"
        )
        
        if output.status != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Practice set creation failed: {output.error}"
            )
        
        return {
            "success": True,
            "task_id": output.task_id,
            "processing_time_ms": output.execution_time_ms,
            **output.result
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating practice set: {str(e)}")


@router.get("/questions/types")
async def get_question_types():
    """
    Get available question types and their descriptions.
    """
    return {
        "question_types": [
            {
                "type": "mcq",
                "name": "Multiple Choice",
                "description": "4 options with one correct answer",
                "features": ["Options A-D", "Correct answer", "Hint"]
            },
            {
                "type": "short_answer",
                "name": "Short Answer",
                "description": "Open-ended questions requiring 1-3 sentences",
                "features": ["Expected answer", "Hint"]
            },
            {
                "type": "fill_blank",
                "name": "Fill in the Blank",
                "description": "Complete the sentence with missing word/phrase",
                "features": ["Sentence with blank", "Correct answer", "Hint"]
            }
        ],
        "difficulty_levels": ["easy", "medium", "hard"],
        "grade_range": [1, 8]
    }


# ============= INTEGRATED WORKFLOW ENDPOINT =============

@router.post("/workflow/material-to-practice")
async def material_to_practice_workflow(
    file: UploadFile = File(..., description="Study material (PDF or image)"),
    subject: str = Form(..., description="Subject area"),
    grade: int = Form(..., description="Grade level (1-8)"),
    topic: Optional[str] = Form(None, description="Specific topic (optional)"),
    question_count: int = Form(default=10, description="Number of questions"),
    question_types: str = Form(default="mcq,short_answer", description="Question types"),
    difficulty: str = Form(default="medium", description="Difficulty level"),
    user_id: str = Form(..., description="User ID"),
    current_user: User = Depends(require_pro_subscription)  # 🔒 PRO REQUIRED
):
    """
    **Complete Workflow: Upload Material → Generate Practice Questions**
    
    **🌟 PRO FEATURE - Requires Pro or Premium subscription**
    
    This endpoint orchestrates all 3 agents:
    1. **Ingestion Agent**: Process and chunk the material
    2. **Retrieval Agent**: Create searchable index
    3. **Question Generator**: Create practice questions
    
    **Perfect for:**
    - Quick practice set creation from any material
    - One-click homework generation
    - Study guide creation
    
    **Example:**
    Upload a PDF about "Photosynthesis" → Get 10 practice questions instantly!
    """
    file_extension = Path(file.filename).suffix.lower()
    temp_file_path = None
    
    try:
        # Save uploaded file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        import uuid
        material_id = str(uuid.uuid4())
        index_name = f"material_{material_id[:8]}"
        
        # Define complete workflow
        workflow = [
            # Step 1: Ingest material
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
            },
            # Step 2: Create search index
            {
                "agent": "retrieval",
                "input": {
                    "operation": "create_index",
                    "index_name": index_name,
                    "chunks": "${ingestion_result}[chunks]",  # Reference from step 1
                    "force_recreate": True
                },
                "output_key": "index_result"
            },
            # Step 3: Generate questions
            {
                "agent": "question_generator",
                "input": {
                    "operation": "generate_practice_set",
                    "title": f"{subject} Practice - {file.filename}",
                    "chunks": "${ingestion_result}[chunks]",
                    "grade": grade,
                    "subject": subject,
                    "question_types": question_types.split(","),
                    "count": question_count,
                    "difficulty": difficulty
                },
                "output_key": "questions_result"
            }
        ]
        
        # Execute workflow
        result = coordinator.execute_workflow(workflow, user_id=user_id)
        
        if result["status"] != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Workflow failed at step {result.get('failed_step', 'unknown')}: {result.get('error', 'Unknown error')}"
            )
        
        # Extract results
        ingestion = result["results"].get("ingestion_result", {})
        questions = result["results"].get("questions_result", {})
        
        return {
            "success": True,
            "workflow_id": result["workflow_id"],
            "material_id": material_id,
            "index_name": index_name,
            "chunks_created": ingestion.get("total_chunks", 0),
            "topics": ingestion.get("topics", []),
            "questions": questions.get("questions", []),
            "question_count": questions.get("count", 0),
            "metadata": {
                "subject": subject,
                "grade": grade,
                "difficulty": difficulty,
                "filename": file.filename
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Workflow error: {str(e)}")
    finally:
        # Clean up
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                print(f"Warning: Could not delete temp file: {e}")


# ============= BULK UPLOAD WORKFLOW ENDPOINT =============

@router.post("/workflow/bulk-material-to-practice")
async def bulk_material_to_practice_workflow(
    files: List[UploadFile] = File(..., description="Multiple study materials (PDF or images)"),
    subject: str = Form(..., description="Subject area"),
    grade: int = Form(..., description="Grade level (1-8)"),
    topic: Optional[str] = Form(None, description="Specific topic (optional)"),
    question_count: int = Form(default=5, description="Questions per file"),
    question_types: str = Form(default="mcq,short_answer", description="Question types"),
    difficulty: str = Form(default="medium", description="Difficulty level"),
    user_id: str = Form(..., description="User ID"),
    current_user: User = Depends(require_pro_subscription)
):
    """
    **Bulk Upload Workflow: Upload Multiple Materials -> Generate Practice Questions**

    Processes multiple study material files in sequence. Each file goes through:
    1. **Ingestion Agent**: Process and chunk the material
    2. **Retrieval Agent**: Create searchable index
    3. **Question Generator**: Create practice questions

    Returns combined results with per-file summaries and a merged question set.
    """
    if not files or len(files) == 0:
        raise HTTPException(status_code=400, detail="No files provided")

    if len(files) > 10:
        raise HTTPException(status_code=400, detail="Maximum 10 files allowed per bulk upload")

    all_questions = []
    file_results = []
    all_topics = []
    total_chunks = 0
    failed_files = []

    for file in files:
        file_extension = Path(file.filename).suffix.lower()
        temp_file_path = None

        try:
            # Save uploaded file
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
                content = await file.read()
                if len(content) > 10 * 1024 * 1024:
                    failed_files.append({
                        "filename": file.filename,
                        "error": "File exceeds 10MB limit"
                    })
                    continue
                temp_file.write(content)
                temp_file_path = temp_file.name

            import uuid
            material_id = str(uuid.uuid4())
            index_name = f"material_{material_id[:8]}"

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
                },
                {
                    "agent": "retrieval",
                    "input": {
                        "operation": "create_index",
                        "index_name": index_name,
                        "chunks": "${ingestion_result}[chunks]",
                        "force_recreate": True
                    },
                    "output_key": "index_result"
                },
                {
                    "agent": "question_generator",
                    "input": {
                        "operation": "generate_practice_set",
                        "title": f"{subject} Practice - {file.filename}",
                        "chunks": "${ingestion_result}[chunks]",
                        "grade": grade,
                        "subject": subject,
                        "question_types": question_types.split(","),
                        "count": question_count,
                        "difficulty": difficulty
                    },
                    "output_key": "questions_result"
                }
            ]

            result = coordinator.execute_workflow(workflow, user_id=user_id)

            if result["status"] != "success":
                failed_files.append({
                    "filename": file.filename,
                    "error": f"Workflow failed: {result.get('error', 'Unknown error')}"
                })
                continue

            ingestion = result["results"].get("ingestion_result", {})
            questions = result["results"].get("questions_result", {})

            file_questions = questions.get("questions", [])
            file_topics = ingestion.get("topics", [])
            file_chunks = ingestion.get("total_chunks", 0)

            all_questions.extend(file_questions)
            all_topics.extend(file_topics)
            total_chunks += file_chunks

            file_results.append({
                "filename": file.filename,
                "material_id": material_id,
                "index_name": index_name,
                "chunks_created": file_chunks,
                "topics": file_topics,
                "questions_generated": len(file_questions),
                "status": "success"
            })

        except Exception as e:
            logger.error(f"Error processing file {file.filename}: {str(e)}")
            failed_files.append({
                "filename": file.filename,
                "error": str(e)
            })
        finally:
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception:
                    pass

    if not file_results and failed_files:
        raise HTTPException(
            status_code=500,
            detail=f"All files failed to process: {failed_files}"
        )

    unique_topics = list(dict.fromkeys(all_topics))

    return {
        "success": True,
        "files_processed": len(file_results),
        "files_failed": len(failed_files),
        "total_chunks": total_chunks,
        "topics": unique_topics,
        "questions": all_questions,
        "question_count": len(all_questions),
        "file_results": file_results,
        "failed_files": failed_files,
        "metadata": {
            "subject": subject,
            "grade": grade,
            "difficulty": difficulty,
            "questions_per_file": question_count
        }
    }


# ============= EXAM GRADING ENDPOINTS (Phase 4) =============

@router.post("/exams/grade")
async def grade_exam(
    questions: str = Form(..., description="JSON array of questions with student answers"),
    student_id: Optional[str] = Form(None, description="Student ID"),
    exam_id: Optional[str] = Form(None, description="Exam ID"),
    subject: Optional[str] = Form(None, description="Subject for persistence"),
    db: Session = Depends(get_db)
):
    """
    Auto-grade an exam with student answers.
    
    **Question Format:**
    ```json
    [
      {
        "type": "mcq",
        "question": "What is 2+2?",
        "options": {"A": "3", "B": "4", "C": "5", "D": "6"},
        "correct_answer": "B",
        "student_answer": "B"
      },
      {
        "type": "short_answer",
        "question": "Explain photosynthesis",
        "expected_answer": "Process by which plants make food...",
        "student_answer": "Plants use sunlight to make food..."
      }
    ]
    ```
    
    **Returns:**
    - Graded questions with scores and feedback
    - Total score and percentage
    - Letter grade (A-F)
    - Knowledge gaps identified
    - Personalized recommendations
    """
    import json
    
    try:
        # Parse questions JSON
        questions_list = json.loads(questions)
        
        # Execute exam analysis agent
        output = exam_analysis_agent.execute(
            input_data={
                "operation": "grade_exam",
                "questions": questions_list,
                "student_id": student_id,
                "exam_id": exam_id
            },
            user_id=student_id,
            related_entity="exams",
            related_id=exam_id
        )
        
        if output.status != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Grading failed: {output.error}"
            )
        
        result = output.result

        # Persist exam results to database
        try:
            import json as json_mod
            recommendations_text = ""
            if isinstance(result.get("recommendations"), list):
                recommendations_text = "\n".join(result["recommendations"])
            elif isinstance(result.get("recommendations"), str):
                recommendations_text = result["recommendations"]

            exam_record = Exam(
                user_id=student_id or "guest",
                title=f"Practice Exam - {subject or 'General'}",
                subject=subject,
                total_score=result.get("total_score"),
                max_score=result.get("max_score"),
                percentage=result.get("percentage"),
                letter_grade=result.get("grade"),
                feedback=result.get("feedback"),
                recommendations=recommendations_text,
                knowledge_gaps_json=result.get("knowledge_gaps"),
                source_type="practice"
            )
            db.add(exam_record)
            db.flush()

            for idx, gq in enumerate(result.get("graded_questions", [])):
                answer_record = ExamAnswer(
                    exam_id=exam_record.id,
                    question_number=idx + 1,
                    question_type=gq.get("type"),
                    question_text=gq.get("question"),
                    student_answer=gq.get("student_answer"),
                    correct_answer=gq.get("correct_answer") or gq.get("expected_answer"),
                    score=gq.get("score"),
                    max_score=gq.get("max_score"),
                    is_correct=gq.get("is_correct"),
                    feedback=gq.get("feedback"),
                    similarity=gq.get("similarity")
                )
                db.add(answer_record)

            db.commit()
            result["exam_record_id"] = exam_record.id
        except Exception as persist_err:
            logger.warning(f"Failed to persist exam results: {persist_err}")
            db.rollback()

        return {
            "success": True,
            "task_id": output.task_id,
            "processing_time_ms": output.execution_time_ms,
            **result
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error grading exam: {str(e)}")


@router.post("/exams/quick-grade")
async def quick_grade_question(
    question_type: str = Form(..., description="Question type: mcq, short_answer, fill_blank"),
    question: str = Form(..., description="Question text"),
    student_answer: str = Form(..., description="Student's answer"),
    correct_answer: str = Form(..., description="Correct answer"),
    expected_answer: Optional[str] = Form(None, description="Expected answer (for short_answer)"),
    options: Optional[str] = Form(None, description="JSON object of options (for mcq)")
):
    """
    Quick grade a single question.
    
    **Perfect for:**
    - Testing individual questions
    - Real-time feedback during practice
    - Quick validation
    
    **Example:**
    ```
    question_type: "mcq"
    question: "What is 2+2?"
    student_answer: "B"
    correct_answer: "B"
    options: '{"A":"3","B":"4","C":"5","D":"6"}'
    ```
    """
    import json
    
    try:
        # Build question object
        question_obj = {
            "type": question_type,
            "question": question,
            "student_answer": student_answer,
            "correct_answer": correct_answer
        }
        
        if question_type == "mcq" and options:
            question_obj["options"] = json.loads(options)
        
        if question_type == "short_answer" and expected_answer:
            question_obj["expected_answer"] = expected_answer
        
        # Grade single question
        output = exam_analysis_agent.execute(
            input_data={
                "operation": "grade_exam",
                "questions": [question_obj]
            },
            related_entity="quick_grade",
            related_id="single"
        )
        
        if output.status != "success":
            raise HTTPException(
                status_code=500,
                detail=f"Grading failed: {output.error}"
            )
        
        result = output.result
        graded_question = result["graded_questions"][0] if result["graded_questions"] else {}
        
        return {
            "success": True,
            "score": graded_question.get("score", 0),
            "max_score": graded_question.get("max_score", 1),
            "is_correct": graded_question.get("is_correct", False),
            "feedback": graded_question.get("feedback", "No feedback available"),
            "processing_time_ms": output.execution_time_ms
        }
        
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON in options: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error grading question: {str(e)}")


@router.get("/exams/grading-info")
async def get_grading_info():
    """
    Get information about grading methods and scoring.
    """
    return {
        "grading_methods": {
            "mcq": {
                "method": "Exact match",
                "scoring": "1 point for correct, 0 for incorrect",
                "feedback": "Automatic with correct answer shown"
            },
            "fill_blank": {
                "method": "Similarity matching",
                "scoring": "1 point if >80% similar, 0.5 if >60% similar, 0 otherwise",
                "feedback": "Shows similarity percentage and correct answer"
            },
            "short_answer": {
                "method": "AI evaluation",
                "scoring": "0.0 to 1.0 based on AI assessment",
                "feedback": "Detailed AI-generated feedback"
            }
        },
        "letter_grades": {
            "A": "90-100%",
            "B": "80-89%",
            "C": "70-79%",
            "D": "60-69%",
            "F": "0-59%"
        },
        "features": [
            "Auto-grading for all question types",
            "Detailed feedback per question",
            "Knowledge gap identification",
            "Personalized recommendations",
            "Performance metrics"
        ]
    }


# ============= EXAM HISTORY ENDPOINTS =============

@router.get("/exams/history")
async def get_exam_history(
    user_id: str = Query(..., description="User ID"),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get exam history for a user."""
    exams = db.query(Exam)\
        .filter(Exam.user_id == user_id)\
        .order_by(Exam.created_at.desc())\
        .limit(limit)\
        .all()

    return {
        "total": len(exams),
        "exams": [
            {
                "id": exam.id,
                "title": exam.title,
                "subject": exam.subject,
                "total_score": exam.total_score,
                "max_score": exam.max_score,
                "percentage": exam.percentage,
                "letter_grade": exam.letter_grade,
                "source_type": exam.source_type,
                "created_at": exam.created_at.isoformat() if exam.created_at else None
            }
            for exam in exams
        ]
    }


@router.get("/exams/{exam_id}/details")
async def get_exam_details(
    exam_id: str,
    db: Session = Depends(get_db)
):
    """Get detailed exam results including all answers."""
    exam = db.query(Exam).filter(Exam.id == exam_id).first()
    if not exam:
        raise HTTPException(status_code=404, detail="Exam not found")

    return {
        "id": exam.id,
        "title": exam.title,
        "subject": exam.subject,
        "total_score": exam.total_score,
        "max_score": exam.max_score,
        "percentage": exam.percentage,
        "letter_grade": exam.letter_grade,
        "feedback": exam.feedback,
        "recommendations": exam.recommendations,
        "knowledge_gaps": exam.knowledge_gaps_json,
        "source_type": exam.source_type,
        "created_at": exam.created_at.isoformat() if exam.created_at else None,
        "answers": [
            {
                "question_number": a.question_number,
                "question_type": a.question_type,
                "question_text": a.question_text,
                "student_answer": a.student_answer,
                "correct_answer": a.correct_answer,
                "score": a.score,
                "max_score": a.max_score,
                "is_correct": a.is_correct,
                "feedback": a.feedback
            }
            for a in sorted(exam.answers, key=lambda x: x.question_number or 0)
        ]
    }


# ============= ASSIGNMENT CRUD ENDPOINTS =============

@router.get("/assignments")
async def get_assignments(
    user_id: str = Query(..., description="User ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    db: Session = Depends(get_db)
):
    """Get assignments for a user."""
    query = db.query(Assignment).filter(Assignment.user_id == user_id)
    if status:
        query = query.filter(Assignment.status == status)
    assignments = query.order_by(Assignment.due_date.asc()).all()

    return {
        "total": len(assignments),
        "assignments": [
            {
                "id": a.id,
                "title": a.title,
                "subject": a.subject,
                "description": a.description,
                "due_date": a.due_date.isoformat() if a.due_date else None,
                "status": a.status,
                "file_name": a.file_name,
                "created_at": a.created_at.isoformat() if a.created_at else None
            }
            for a in assignments
        ]
    }


@router.post("/assignments")
async def create_assignment(
    title: str = Form(..., description="Assignment title"),
    subject: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    due_date: Optional[str] = Form(None, description="ISO date string"),
    user_id: str = Form(...),
    file: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """Create a new assignment."""
    from datetime import datetime as dt
    import uuid

    file_url = None
    file_name = None
    if file:
        os.makedirs("static/assignments", exist_ok=True)
        ext = Path(file.filename).suffix.lower()
        file_name = file.filename
        saved_name = f"{uuid.uuid4()}{ext}"
        file_url = f"static/assignments/{saved_name}"
        content = await file.read()
        with open(file_url, "wb") as f:
            f.write(content)

    parsed_due = None
    if due_date:
        try:
            parsed_due = dt.fromisoformat(due_date)
        except ValueError:
            pass

    assignment = Assignment(
        user_id=user_id,
        title=title,
        subject=subject,
        description=description,
        due_date=parsed_due,
        file_url=file_url,
        file_name=file_name
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)

    return {
        "success": True,
        "assignment": {
            "id": assignment.id,
            "title": assignment.title,
            "subject": assignment.subject,
            "due_date": assignment.due_date.isoformat() if assignment.due_date else None,
            "status": assignment.status
        }
    }


@router.put("/assignments/{assignment_id}/status")
async def update_assignment_status(
    assignment_id: str,
    status: str = Form(..., description="New status: pending, in_progress, completed"),
    db: Session = Depends(get_db)
):
    """Update assignment status."""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if status not in ("pending", "in_progress", "completed"):
        raise HTTPException(status_code=400, detail="Invalid status")

    assignment.status = status
    db.commit()

    return {"success": True, "status": assignment.status}


@router.delete("/assignments/{assignment_id}")
async def delete_assignment(
    assignment_id: str,
    db: Session = Depends(get_db)
):
    """Delete an assignment."""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    if assignment.file_url and os.path.exists(assignment.file_url):
        try:
            os.unlink(assignment.file_url)
        except Exception:
            pass

    db.delete(assignment)
    db.commit()

    return {"success": True}


# ============= PROGRESS / STATS ENDPOINT =============

@router.get("/stats")
async def get_homework_stats(
    user_id: str = Query(..., description="User ID"),
    db: Session = Depends(get_db)
):
    """Get homework stats for progress widget."""
    from datetime import datetime as dt, timedelta
    week_ago = dt.utcnow() - timedelta(days=7)

    total_exams = db.query(Exam).filter(
        Exam.user_id == user_id,
        Exam.created_at >= week_ago
    ).count()

    total_assignments = db.query(Assignment).filter(Assignment.user_id == user_id).count()
    completed_assignments = db.query(Assignment).filter(
        Assignment.user_id == user_id,
        Assignment.status == "completed"
    ).count()

    recent_exams = db.query(Exam).filter(
        Exam.user_id == user_id
    ).order_by(Exam.created_at.desc()).limit(5).all()

    avg_score = 0
    if recent_exams:
        scores = [e.percentage for e in recent_exams if e.percentage is not None]
        avg_score = sum(scores) / len(scores) if scores else 0

    total_questions = db.query(ExamAnswer).join(Exam).filter(
        Exam.user_id == user_id
    ).count()

    return {
        "weekly_exams": total_exams,
        "total_assignments": total_assignments,
        "completed_assignments": completed_assignments,
        "average_score": round(avg_score, 1),
        "total_questions_answered": total_questions,
        "tests_analyzed": db.query(Exam).filter(Exam.user_id == user_id).count()
    }


# Register agents with coordinator
coordinator.register_agent(ingestion_agent)
coordinator.register_agent(retrieval_agent)
coordinator.register_agent(question_generator_agent)
coordinator.register_agent(exam_analysis_agent)


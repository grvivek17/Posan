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
from app.agents.retrieval_agent import retrieval_agent
from app.agents.question_generator_agent import question_generator_agent
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
    difficulty: str = Form(default="medium", description="Difficulty level")
):
    """
    Generate practice questions from text context.
    
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
    user_id: str = Form(..., description="User ID")
):
    """
    **Complete Workflow: Upload Material → Generate Practice Questions**
    
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


# Register agents with coordinator
coordinator.register_agent(ingestion_agent)
coordinator.register_agent(retrieval_agent)
coordinator.register_agent(question_generator_agent)


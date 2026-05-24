"""
Base Agent Framework for Multi-Agent Homework System

This module provides the foundation for all agents in the system:
- Standardized logging and traceability
- Error handling and retry mechanisms
- Input/output validation
- Performance monitoring
"""

import uuid
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)


class AgentStatus(str, Enum):
    """Agent execution status"""
    SUCCESS = "success"
    FAILURE = "failure"
    PARTIAL = "partial"
    RUNNING = "running"


class AgentInput(BaseModel):
    """Base input schema for all agents"""
    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentOutput(BaseModel):
    """Base output schema for all agents"""
    task_id: str
    status: AgentStatus
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)
    execution_time_ms: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AgentRun(BaseModel):
    """Agent execution log entry"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    agent_name: str
    task_id: str
    input_json: Dict[str, Any]
    output_json: Optional[Dict[str, Any]] = None
    status: AgentStatus
    error: Optional[str] = None
    user_id: Optional[str] = None
    related_entity: Optional[str] = None
    related_id: Optional[str] = None
    execution_time_ms: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AgentBase:
    """
    Base class for all agents in the system.
    
    Provides:
    - Standardized execution flow
    - Automatic logging and traceability
    - Error handling with retries
    - Performance monitoring
    """
    
    def __init__(self, name: str, max_retries: int = 3):
        """
        Initialize agent.
        
        Args:
            name: Agent name (e.g., "ingestion", "retrieval", "question_generator")
            max_retries: Maximum number of retry attempts on failure
        """
        self.name = name
        self.max_retries = max_retries
        self.logger = logging.getLogger(f"agent.{name}")
        self.runs: List[AgentRun] = []  # In-memory log (will be persisted to DB)
    
    def execute(
        self,
        input_data: Dict[str, Any],
        user_id: Optional[str] = None,
        related_entity: Optional[str] = None,
        related_id: Optional[str] = None
    ) -> AgentOutput:
        """
        Execute agent task with logging and error handling.
        
        Args:
            input_data: Task input data
            user_id: User ID for tracking
            related_entity: Related entity type (e.g., "materials", "exams")
            related_id: Related entity ID
            
        Returns:
            AgentOutput with results or error information
        """
        task_id = str(uuid.uuid4())
        start_time = datetime.utcnow()
        
        self.logger.info(f"Starting task {task_id} for agent {self.name}")
        
        # Create agent run log
        agent_run = AgentRun(
            agent_name=self.name,
            task_id=task_id,
            input_json=input_data,
            status=AgentStatus.RUNNING,
            user_id=user_id,
            related_entity=related_entity,
            related_id=related_id
        )
        
        attempt = 0
        last_error = None
        
        while attempt < self.max_retries:
            try:
                # Execute the agent's core logic
                result = self._execute_task(input_data)
                
                # Calculate execution time
                execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                
                # Create successful output
                output = AgentOutput(
                    task_id=task_id,
                    status=AgentStatus.SUCCESS,
                    result=result,
                    execution_time_ms=execution_time
                )
                
                # Update agent run log
                agent_run.status = AgentStatus.SUCCESS
                agent_run.output_json = result
                agent_run.execution_time_ms = execution_time
                
                self.logger.info(
                    f"Task {task_id} completed successfully in {execution_time:.2f}ms"
                )
                
                self.runs.append(agent_run)
                self._persist_run(agent_run)
                return output
                
            except Exception as e:
                attempt += 1
                last_error = str(e)
                self.logger.error(
                    f"Task {task_id} attempt {attempt}/{self.max_retries} failed: {e}"
                )
                
                if attempt >= self.max_retries:
                    # All retries exhausted
                    execution_time = (datetime.utcnow() - start_time).total_seconds() * 1000
                    
                    output = AgentOutput(
                        task_id=task_id,
                        status=AgentStatus.FAILURE,
                        error=last_error,
                        execution_time_ms=execution_time,
                        confidence=0.0
                    )
                    
                    agent_run.status = AgentStatus.FAILURE
                    agent_run.error = last_error
                    agent_run.execution_time_ms = execution_time
                    
                    self.runs.append(agent_run)
                    self._persist_run(agent_run)
                    return output
    
    def _execute_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Core task execution logic. Must be implemented by subclasses.
        
        Args:
            input_data: Task input data
            
        Returns:
            Task result as dictionary
            
        Raises:
            NotImplementedError: If not implemented by subclass
        """
        raise NotImplementedError(
            f"Agent {self.name} must implement _execute_task method"
        )
    
    def _persist_run(self, agent_run: 'AgentRun'):
        """Persist agent run to database (best-effort, non-blocking)."""
        try:
            from app.core.database import SessionLocal
            from app.services.material_service import agent_log_service
            db = SessionLocal()
            try:
                agent_log_service.log_agent_run(db, agent_run)
            finally:
                db.close()
        except Exception as e:
            self.logger.warning(f"Failed to persist agent run to DB: {e}")
    
    def get_runs(self, limit: int = 10) -> List[AgentRun]:
        """
        Get recent agent runs.
        
        Args:
            limit: Maximum number of runs to return
            
        Returns:
            List of recent agent runs
        """
        return self.runs[-limit:]
    
    def get_run_by_task_id(self, task_id: str) -> Optional[AgentRun]:
        """
        Get agent run by task ID.
        
        Args:
            task_id: Task ID to search for
            
        Returns:
            AgentRun if found, None otherwise
        """
        for run in reversed(self.runs):
            if run.task_id == task_id:
                return run
        return None
    
    def clear_runs(self):
        """Clear all agent runs from memory."""
        self.runs.clear()
        self.logger.info(f"Cleared all runs for agent {self.name}")


class CoordinatorAgent(AgentBase):
    """
    Coordinator agent that orchestrates multiple agents.
    
    Responsibilities:
    - Task routing to appropriate agents
    - Dependency management
    - Fallback handling
    - Workflow orchestration
    """
    
    def __init__(self):
        super().__init__(name="coordinator", max_retries=1)
        self.agents: Dict[str, AgentBase] = {}
    
    def register_agent(self, agent: AgentBase):
        """
        Register an agent with the coordinator.
        
        Args:
            agent: Agent instance to register
        """
        self.agents[agent.name] = agent
        self.logger.info(f"Registered agent: {agent.name}")
    
    def get_agent(self, name: str) -> Optional[AgentBase]:
        """
        Get registered agent by name.
        
        Args:
            name: Agent name
            
        Returns:
            Agent instance if found, None otherwise
        """
        return self.agents.get(name)
    
    def execute_workflow(
        self,
        workflow: List[Dict[str, Any]],
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a workflow of agent tasks.
        
        Args:
            workflow: List of task definitions with agent names and inputs
            user_id: User ID for tracking
            
        Returns:
            Workflow execution results
            
        Example workflow:
            [
                {
                    "agent": "ingestion",
                    "input": {"file_path": "/path/to/file.pdf"},
                    "output_key": "chunks"
                },
                {
                    "agent": "retrieval",
                    "input": {"chunks": "${chunks}", "query": "math"},
                    "output_key": "relevant_chunks"
                }
            ]
        """
        workflow_id = str(uuid.uuid4())
        results = {}
        
        self.logger.info(f"Starting workflow {workflow_id} with {len(workflow)} steps")
        
        for step_idx, step in enumerate(workflow):
            agent_name = step.get("agent")
            input_data = step.get("input", {})
            output_key = step.get("output_key", f"step_{step_idx}")
            
            # Get agent
            agent = self.get_agent(agent_name)
            if not agent:
                error_msg = f"Agent {agent_name} not found"
                self.logger.error(error_msg)
                return {
                    "workflow_id": workflow_id,
                    "status": "failure",
                    "error": error_msg,
                    "completed_steps": step_idx,
                    "results": results
                }
            
            # Resolve input variables from previous steps
            resolved_input = self._resolve_variables(input_data, results)
            
            # Execute agent task
            output = agent.execute(
                input_data=resolved_input,
                user_id=user_id,
                related_entity="workflow",
                related_id=workflow_id
            )
            
            # Check for failure
            if output.status == AgentStatus.FAILURE:
                self.logger.error(
                    f"Workflow {workflow_id} failed at step {step_idx} ({agent_name})"
                )
                return {
                    "workflow_id": workflow_id,
                    "status": "failure",
                    "error": output.error,
                    "failed_step": step_idx,
                    "failed_agent": agent_name,
                    "completed_steps": step_idx,
                    "results": results
                }
            
            # Store result
            results[output_key] = output.result
        
        self.logger.info(f"Workflow {workflow_id} completed successfully")
        
        return {
            "workflow_id": workflow_id,
            "status": "success",
            "completed_steps": len(workflow),
            "results": results
        }
    
    def _resolve_variables(
        self,
        input_data: Dict[str, Any],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Resolve variable references in input data.
        
        Variables are referenced as ${variable_name} or ${variable_name}[key].
        
        Args:
            input_data: Input data with potential variable references
            context: Context dictionary with variable values
            
        Returns:
            Resolved input data
        """
        import re
        
        resolved = {}
        
        for key, value in input_data.items():
            if isinstance(value, str) and "${" in value:
                # Check for nested path like ${var}[key]
                pattern = r'\$\{([^}]+)\}(?:\[([^\]]+)\])?'
                match = re.match(pattern, value)
                
                if match:
                    var_name = match.group(1)
                    nested_key = match.group(2)
                    
                    # Get base value
                    base_value = context.get(var_name)
                    
                    # Access nested key if specified
                    if nested_key and base_value:
                        if isinstance(base_value, dict):
                            resolved[key] = base_value.get(nested_key)
                        else:
                            resolved[key] = base_value
                    else:
                        resolved[key] = base_value
                else:
                    resolved[key] = value
            else:
                resolved[key] = value
        
        return resolved


# Global coordinator instance
coordinator = CoordinatorAgent()

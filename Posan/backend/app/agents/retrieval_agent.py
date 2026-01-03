"""
Retrieval Agent - Semantic Search over Study Materials

Responsibilities:
- Generate embeddings for text chunks
- Create and manage FAISS indices
- Perform semantic search
- Multi-level indexing (material, subject, topic, grade)
- Top-k retrieval with relevance scoring
"""

from typing import Dict, Any, List, Optional
import logging

from app.agents import AgentBase
from app.services.vector_store import vector_store

logger = logging.getLogger(__name__)


class RetrievalAgent(AgentBase):
    """
    Agent for semantic search and retrieval.
    
    Features:
    - Embedding generation
    - FAISS index creation
    - Semantic search
    - Multi-index search
    - Relevance scoring
    """
    
    def __init__(self):
        super().__init__(name="retrieval", max_retries=2)
        self.vector_store = vector_store
    
    def _execute_task(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute retrieval task.
        
        Supported operations:
        - create_index: Create FAISS index from chunks
        - search: Semantic search in an index
        - search_multi: Search across multiple indices
        - add_chunks: Add chunks to existing index
        - delete_index: Delete an index
        - list_indices: List all indices
        
        Input (create_index):
            - operation: "create_index"
            - index_name: Name for the index
            - chunks: List of chunk dictionaries
            - force_recreate: Optional, recreate if exists
            
        Input (search):
            - operation: "search"
            - index_name: Index to search
            - query: Search query
            - top_k: Number of results (default: 5)
            - min_score: Minimum similarity score (default: 0.0)
            
        Input (search_multi):
            - operation: "search_multi"
            - index_names: List of indices to search
            - query: Search query
            - top_k: Number of results (default: 5)
            - min_score: Minimum similarity score (default: 0.0)
            
        Output:
            Depends on operation
        """
        operation = input_data.get("operation")
        
        if not operation:
            raise ValueError("'operation' is required")
        
        if operation == "create_index":
            return self._create_index(input_data)
        
        elif operation == "search":
            return self._search(input_data)
        
        elif operation == "search_multi":
            return self._search_multi(input_data)
        
        elif operation == "add_chunks":
            return self._add_chunks(input_data)
        
        elif operation == "delete_index":
            return self._delete_index(input_data)
        
        elif operation == "list_indices":
            return self._list_indices(input_data)
        
        else:
            raise ValueError(f"Unknown operation: {operation}")
    
    def _create_index(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create FAISS index from chunks"""
        index_name = input_data.get("index_name")
        chunks = input_data.get("chunks", [])
        force_recreate = input_data.get("force_recreate", False)
        
        if not index_name:
            raise ValueError("'index_name' is required")
        
        if not chunks:
            raise ValueError("'chunks' list is required")
        
        self.logger.info(f"Creating index '{index_name}' with {len(chunks)} chunks")
        
        result = self.vector_store.create_index(
            index_name=index_name,
            chunks=chunks,
            force_recreate=force_recreate
        )
        
        return result
    
    def _search(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search in a single index"""
        index_name = input_data.get("index_name")
        query = input_data.get("query")
        top_k = input_data.get("top_k", 5)
        min_score = input_data.get("min_score", 0.0)
        
        if not index_name:
            raise ValueError("'index_name' is required")
        
        if not query:
            raise ValueError("'query' is required")
        
        self.logger.info(f"Searching in '{index_name}' for: {query[:50]}...")
        
        results = self.vector_store.search(
            index_name=index_name,
            query=query,
            top_k=top_k,
            min_score=min_score
        )
        
        return {
            "query": query,
            "index_name": index_name,
            "results": results,
            "count": len(results)
        }
    
    def _search_multi(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Search across multiple indices"""
        index_names = input_data.get("index_names", [])
        query = input_data.get("query")
        top_k = input_data.get("top_k", 5)
        min_score = input_data.get("min_score", 0.0)
        
        if not index_names:
            raise ValueError("'index_names' list is required")
        
        if not query:
            raise ValueError("'query' is required")
        
        self.logger.info(
            f"Searching in {len(index_names)} indices for: {query[:50]}..."
        )
        
        results = self.vector_store.search_multi_index(
            index_names=index_names,
            query=query,
            top_k=top_k,
            min_score=min_score
        )
        
        return {
            "query": query,
            "index_names": index_names,
            "results": results,
            "count": len(results)
        }
    
    def _add_chunks(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add chunks to existing index"""
        index_name = input_data.get("index_name")
        chunks = input_data.get("chunks", [])
        
        if not index_name:
            raise ValueError("'index_name' is required")
        
        if not chunks:
            raise ValueError("'chunks' list is required")
        
        self.logger.info(f"Adding {len(chunks)} chunks to '{index_name}'")
        
        result = self.vector_store.add_to_index(
            index_name=index_name,
            chunks=chunks
        )
        
        return result
    
    def _delete_index(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Delete an index"""
        index_name = input_data.get("index_name")
        
        if not index_name:
            raise ValueError("'index_name' is required")
        
        self.logger.info(f"Deleting index '{index_name}'")
        
        deleted = self.vector_store.delete_index(index_name)
        
        return {
            "index_name": index_name,
            "deleted": deleted
        }
    
    def _list_indices(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """List all indices"""
        self.logger.info("Listing all indices")
        
        indices = self.vector_store.list_indices()
        
        return {
            "indices": indices,
            "count": len(indices)
        }


# Global retrieval agent instance
retrieval_agent = RetrievalAgent()

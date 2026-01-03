"""
Vector Store Service using FAISS

Handles:
- Embedding generation using sentence-transformers
- FAISS index management
- Semantic search
- Multi-level indexing (material, subject, topic, grade)
"""

import os
import pickle
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class VectorStore:
    """
    Vector store for semantic search using FAISS.
    
    Features:
    - Embedding generation with sentence-transformers
    - FAISS index for fast similarity search
    - Persistent storage
    - Multi-index support (by subject, grade, etc.)
    """
    
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        index_dir: str = "vector_indices"
    ):
        """
        Initialize vector store.
        
        Args:
            model_name: Sentence transformer model name
            index_dir: Directory to store FAISS indices
        """
        self.model_name = model_name
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(exist_ok=True)
        
        self.model = None
        self.dimension = 384  # all-MiniLM-L6-v2 dimension
        self.indices = {}  # Store multiple indices
        self.metadata = {}  # Store metadata for each index
        
        logger.info(f"VectorStore initialized with model: {model_name}")
    
    def _load_model(self):
        """Lazy load the sentence transformer model"""
        if self.model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"Loading model: {self.model_name}")
                self.model = SentenceTransformer(self.model_name)
                logger.info("Model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load model: {e}")
                raise
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a list of texts.
        
        Args:
            texts: List of text strings
            
        Returns:
            Numpy array of embeddings (n_texts, dimension)
        """
        self._load_model()
        
        if not texts:
            return np.array([])
        
        logger.info(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.model.encode(texts, show_progress_bar=False)
        
        return np.array(embeddings).astype('float32')
    
    def create_index(
        self,
        index_name: str,
        chunks: List[Dict[str, Any]],
        force_recreate: bool = False
    ) -> Dict[str, Any]:
        """
        Create a FAISS index from chunks.
        
        Args:
            index_name: Name for the index (e.g., "material_123", "subject_math")
            chunks: List of chunk dictionaries with 'text' field
            force_recreate: If True, recreate even if index exists
            
        Returns:
            Index statistics
        """
        try:
            import faiss
        except ImportError:
            raise ImportError("FAISS not installed. Run: pip install faiss-cpu")
        
        # Check if index already exists
        if index_name in self.indices and not force_recreate:
            logger.info(f"Index '{index_name}' already exists")
            return {"status": "exists", "size": len(self.metadata[index_name])}
        
        # Extract texts
        texts = [chunk.get("text", "") for chunk in chunks]
        
        if not texts:
            raise ValueError("No texts provided for indexing")
        
        # Generate embeddings
        embeddings = self.generate_embeddings(texts)
        
        # Create FAISS index
        logger.info(f"Creating FAISS index '{index_name}' with {len(embeddings)} vectors")
        index = faiss.IndexFlatL2(self.dimension)  # L2 distance
        index.add(embeddings)
        
        # Store index and metadata
        self.indices[index_name] = index
        self.metadata[index_name] = chunks
        
        # Save to disk
        self._save_index(index_name)
        
        logger.info(f"Index '{index_name}' created successfully")
        
        return {
            "status": "created",
            "index_name": index_name,
            "size": len(chunks),
            "dimension": self.dimension
        }
    
    def search(
        self,
        index_name: str,
        query: str,
        top_k: int = 5,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for similar chunks using semantic similarity.
        
        Args:
            index_name: Name of the index to search
            query: Query text
            top_k: Number of results to return
            min_score: Minimum similarity score (0-1, higher is more similar)
            
        Returns:
            List of results with chunks and scores
        """
        try:
            import faiss
        except ImportError:
            raise ImportError("FAISS not installed. Run: pip install faiss-cpu")
        
        # Load index if not in memory
        if index_name not in self.indices:
            self._load_index(index_name)
        
        if index_name not in self.indices:
            raise ValueError(f"Index '{index_name}' not found")
        
        # Generate query embedding
        query_embedding = self.generate_embeddings([query])
        
        # Search
        index = self.indices[index_name]
        distances, indices = index.search(query_embedding, top_k)
        
        # Convert distances to similarity scores (0-1, higher is better)
        # L2 distance: convert to similarity using exponential decay
        similarities = np.exp(-distances[0] / 10.0)
        
        # Get results
        results = []
        for idx, (distance, similarity) in enumerate(zip(distances[0], similarities)):
            if similarity >= min_score:
                chunk_idx = indices[0][idx]
                chunk = self.metadata[index_name][chunk_idx]
                
                results.append({
                    "chunk": chunk,
                    "score": float(similarity),
                    "distance": float(distance),
                    "rank": idx + 1
                })
        
        logger.info(f"Search in '{index_name}' returned {len(results)} results")
        
        return results
    
    def search_multi_index(
        self,
        index_names: List[str],
        query: str,
        top_k: int = 5,
        min_score: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search across multiple indices and merge results.
        
        Args:
            index_names: List of index names to search
            query: Query text
            top_k: Total number of results to return
            min_score: Minimum similarity score
            
        Returns:
            Merged and sorted results
        """
        all_results = []
        
        for index_name in index_names:
            try:
                results = self.search(index_name, query, top_k, min_score)
                # Add index name to each result
                for result in results:
                    result["index_name"] = index_name
                all_results.extend(results)
            except Exception as e:
                logger.warning(f"Failed to search index '{index_name}': {e}")
        
        # Sort by score
        all_results.sort(key=lambda x: x["score"], reverse=True)
        
        # Return top_k
        return all_results[:top_k]
    
    def add_to_index(
        self,
        index_name: str,
        chunks: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Add new chunks to an existing index.
        
        Args:
            index_name: Name of the index
            chunks: List of new chunks to add
            
        Returns:
            Update statistics
        """
        try:
            import faiss
        except ImportError:
            raise ImportError("FAISS not installed")
        
        # Load index if not in memory
        if index_name not in self.indices:
            self._load_index(index_name)
        
        if index_name not in self.indices:
            raise ValueError(f"Index '{index_name}' not found")
        
        # Generate embeddings for new chunks
        texts = [chunk.get("text", "") for chunk in chunks]
        embeddings = self.generate_embeddings(texts)
        
        # Add to index
        self.indices[index_name].add(embeddings)
        
        # Update metadata
        self.metadata[index_name].extend(chunks)
        
        # Save
        self._save_index(index_name)
        
        logger.info(f"Added {len(chunks)} chunks to index '{index_name}'")
        
        return {
            "status": "updated",
            "added": len(chunks),
            "total": len(self.metadata[index_name])
        }
    
    def delete_index(self, index_name: str) -> bool:
        """
        Delete an index.
        
        Args:
            index_name: Name of the index to delete
            
        Returns:
            True if deleted, False if not found
        """
        # Remove from memory
        if index_name in self.indices:
            del self.indices[index_name]
        
        if index_name in self.metadata:
            del self.metadata[index_name]
        
        # Remove from disk
        index_path = self.index_dir / f"{index_name}.faiss"
        metadata_path = self.index_dir / f"{index_name}.pkl"
        
        deleted = False
        
        if index_path.exists():
            index_path.unlink()
            deleted = True
        
        if metadata_path.exists():
            metadata_path.unlink()
            deleted = True
        
        if deleted:
            logger.info(f"Deleted index '{index_name}'")
        
        return deleted
    
    def list_indices(self) -> List[Dict[str, Any]]:
        """
        List all available indices.
        
        Returns:
            List of index information
        """
        indices_info = []
        
        # Check disk for saved indices
        for faiss_file in self.index_dir.glob("*.faiss"):
            index_name = faiss_file.stem
            metadata_file = self.index_dir / f"{index_name}.pkl"
            
            info = {
                "name": index_name,
                "in_memory": index_name in self.indices,
                "size": 0
            }
            
            # Get size from metadata
            if metadata_file.exists():
                try:
                    with open(metadata_file, 'rb') as f:
                        metadata = pickle.load(f)
                        info["size"] = len(metadata)
                except Exception as e:
                    logger.warning(f"Failed to load metadata for '{index_name}': {e}")
            
            indices_info.append(info)
        
        return indices_info
    
    def _save_index(self, index_name: str):
        """Save index and metadata to disk"""
        try:
            import faiss
        except ImportError:
            return
        
        index_path = self.index_dir / f"{index_name}.faiss"
        metadata_path = self.index_dir / f"{index_name}.pkl"
        
        # Save FAISS index
        faiss.write_index(self.indices[index_name], str(index_path))
        
        # Save metadata
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata[index_name], f)
        
        logger.debug(f"Saved index '{index_name}' to disk")
    
    def _load_index(self, index_name: str):
        """Load index and metadata from disk"""
        try:
            import faiss
        except ImportError:
            return
        
        index_path = self.index_dir / f"{index_name}.faiss"
        metadata_path = self.index_dir / f"{index_name}.pkl"
        
        if not index_path.exists() or not metadata_path.exists():
            logger.warning(f"Index '{index_name}' not found on disk")
            return
        
        # Load FAISS index
        self.indices[index_name] = faiss.read_index(str(index_path))
        
        # Load metadata
        with open(metadata_path, 'rb') as f:
            self.metadata[index_name] = pickle.load(f)
        
        logger.info(f"Loaded index '{index_name}' from disk")


# Global vector store instance
vector_store = VectorStore()

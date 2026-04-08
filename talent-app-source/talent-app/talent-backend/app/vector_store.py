"""Neural vector store for semantic search over talent profiles.

Uses sentence-transformers (all-MiniLM-L6-v2) for embeddings and FAISS for
fast similarity search. Persists embeddings + metadata to disk as .npy/.json
so it survives restarts.
"""

import os
import json
import logging
import numpy as np

logger = logging.getLogger(__name__)

# Persistent storage directory
VECTOR_STORE_PATH = os.getenv(
    "VECTOR_STORE_PATH",
    os.path.join(os.path.dirname(__file__), "..", "vector_index.json"),
)

# Derive directory and file paths from the legacy path
_STORE_DIR = os.path.dirname(VECTOR_STORE_PATH) or "."
_EMBEDDINGS_PATH = os.path.join(_STORE_DIR, "faiss_embeddings.npy")
_METADATA_PATH = os.path.join(_STORE_DIR, "faiss_metadata.json")

# Lazy-loaded globals
_model = None
_index = None
_metadata: list[dict] = []  # parallel array with FAISS index rows
_loaded = False

MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384


def _get_model():
    """Lazy-load the sentence-transformer model."""
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        logger.info("Loading sentence-transformer model: %s", MODEL_NAME)
        _model = SentenceTransformer(MODEL_NAME)
        logger.info("Model loaded successfully")
    return _model


def _save_store() -> None:
    """Persist FAISS index + metadata to disk."""
    try:
        os.makedirs(_STORE_DIR, exist_ok=True)
        if _index is not None and _index.ntotal > 0:
            vectors = np.zeros((_index.ntotal, EMBEDDING_DIM), dtype=np.float32)
            for i in range(_index.ntotal):
                vectors[i] = _index.reconstruct(i)
            np.save(_EMBEDDINGS_PATH, vectors)
            with open(_METADATA_PATH, "w") as f:
                json.dump(_metadata, f)
            logger.info("Saved %d embeddings to disk", _index.ntotal)
    except Exception as e:
        logger.warning("Failed to save vector store: %s", e)


def _load_store() -> None:
    """Load FAISS index + metadata from disk."""
    global _index, _metadata, _loaded
    if _loaded:
        return

    import faiss

    try:
        if os.path.exists(_EMBEDDINGS_PATH) and os.path.exists(_METADATA_PATH):
            vectors = np.load(_EMBEDDINGS_PATH)
            with open(_METADATA_PATH, "r") as f:
                _metadata = json.load(f)

            if len(vectors) > 0 and len(vectors) == len(_metadata):
                _index = faiss.IndexFlatIP(EMBEDDING_DIM)
                _index.add(vectors.astype(np.float32))
                logger.info("Loaded %d embeddings from disk", _index.ntotal)
            else:
                _index = faiss.IndexFlatIP(EMBEDDING_DIM)
                _metadata = []
        else:
            _index = faiss.IndexFlatIP(EMBEDDING_DIM)
            _metadata = []
    except Exception as e:
        logger.warning("Failed to load vector store, starting fresh: %s", e)
        _index = faiss.IndexFlatIP(EMBEDDING_DIM)
        _metadata = []

    _loaded = True


def _build_profile_document(profile_data: dict) -> str:
    """Build a rich text document from profile data for embedding."""
    parts = []

    name = profile_data.get("name", "")
    if name:
        parts.append(f"Name: {name}")

    summary = profile_data.get("summary", "")
    if summary:
        parts.append(f"Summary: {summary}")

    skills_data = profile_data.get("skills", [])
    if isinstance(skills_data, list):
        for category in skills_data:
            if isinstance(category, dict):
                cat_name = category.get("category", "")
                cat_skills = category.get("skills", [])
                skill_names = []
                for s in cat_skills:
                    if isinstance(s, dict):
                        skill_names.append(s.get("name", ""))
                    elif isinstance(s, str):
                        skill_names.append(s)
                if cat_name and skill_names:
                    parts.append(f"{cat_name}: {', '.join(skill_names)}")

    exp_years = profile_data.get("experience_years")
    if exp_years:
        parts.append(f"Experience: {exp_years} years")

    education = profile_data.get("education", [])
    if education:
        edu_texts = []
        for edu in education:
            if isinstance(edu, dict):
                edu_texts.append(edu.get("degree", ""))
            elif isinstance(edu, str):
                edu_texts.append(edu)
        if edu_texts:
            parts.append(f"Education: {', '.join(edu_texts)}")

    certs = profile_data.get("certifications", [])
    if certs:
        parts.append(f"Certifications: {', '.join(certs)}")

    return "\n".join(parts)


# ── Public API ──

def get_collection() -> None:
    """Initialize the vector store (load from disk)."""
    _load_store()


def add_profile_to_vector_store(profile_id: int, skill_matrix: dict, raw_text: str = "") -> None:
    """Add or update a profile in the vector store."""
    import faiss as _faiss

    _load_store()
    global _index, _metadata

    document = _build_profile_document(skill_matrix)
    if len(document) < 100 and raw_text:
        document += f"\n\nResume Text:\n{raw_text[:2000]}"

    # Flatten skill names for metadata
    all_skills: list[str] = []
    skills_data = skill_matrix.get("skills", [])
    if isinstance(skills_data, list):
        for category in skills_data:
            if isinstance(category, dict):
                for s in category.get("skills", []):
                    if isinstance(s, dict):
                        all_skills.append(s.get("name", "").lower())

    # Remove existing entry for this profile if present
    existing_idx = None
    for i, meta in enumerate(_metadata):
        if meta.get("profile_id") == profile_id:
            existing_idx = i
            break

    if existing_idx is not None:
        _metadata.pop(existing_idx)
        if _index is not None and _index.ntotal > 0:
            vectors = np.zeros((_index.ntotal, EMBEDDING_DIM), dtype=np.float32)
            for i in range(_index.ntotal):
                vectors[i] = _index.reconstruct(i)
            remaining = np.delete(vectors, existing_idx, axis=0)
            _index = _faiss.IndexFlatIP(EMBEDDING_DIM)
            if len(remaining) > 0:
                _index.add(remaining.astype(np.float32))

    # Encode and add
    model = _get_model()
    embedding = model.encode([document], normalize_embeddings=True)
    if _index is None:
        _index = _faiss.IndexFlatIP(EMBEDDING_DIM)
    _index.add(embedding.astype(np.float32))
    _metadata.append({
        "profile_id": profile_id,
        "name": skill_matrix.get("name", "Unknown"),
        "email": skill_matrix.get("email", ""),
        "skills_flat": ", ".join(all_skills),
        "document": document,
    })

    _save_store()
    logger.info("Added profile %d to vector store (total: %d)", profile_id, _index.ntotal)


def remove_profile_from_vector_store(profile_id: int) -> None:
    """Remove a profile from the vector store."""
    import faiss as _faiss

    _load_store()
    global _index, _metadata

    idx_to_remove = None
    for i, meta in enumerate(_metadata):
        if meta.get("profile_id") == profile_id:
            idx_to_remove = i
            break

    if idx_to_remove is not None:
        _metadata.pop(idx_to_remove)
        if _index is not None and _index.ntotal > 0:
            vectors = np.zeros((_index.ntotal, EMBEDDING_DIM), dtype=np.float32)
            for i in range(_index.ntotal):
                vectors[i] = _index.reconstruct(i)
            remaining = np.delete(vectors, idx_to_remove, axis=0)
            _index = _faiss.IndexFlatIP(EMBEDDING_DIM)
            if len(remaining) > 0:
                _index.add(remaining.astype(np.float32))
        _save_store()
        logger.info("Removed profile %d from vector store", profile_id)


def semantic_search(query: str, n_results: int = 10) -> list[dict]:
    """Search for profiles semantically similar to the query.

    Uses neural embeddings for true semantic understanding.
    Returns a list of dicts with: profile_id, name, email, skills_flat,
    distance, similarity, document
    """
    _load_store()

    if _index is None or _index.ntotal == 0:
        return []

    model = _get_model()
    query_embedding = model.encode([query], normalize_embeddings=True)

    k = min(n_results, _index.ntotal)
    scores, indices = _index.search(query_embedding.astype(np.float32), k)

    matches = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0 or idx >= len(_metadata):
            continue
        meta = _metadata[idx]
        similarity = float(score)
        if similarity <= 0:
            continue
        matches.append({
            "profile_id": meta["profile_id"],
            "name": meta.get("name", "Unknown"),
            "email": meta.get("email", ""),
            "skills_flat": meta.get("skills_flat", ""),
            "distance": round(1 - similarity, 4),
            "similarity": round(similarity, 4),
            "document": meta.get("document", ""),
        })

    return matches


def rebuild_vector_store_from_profiles(profiles: list[dict]) -> int:
    """Rebuild the entire vector store from a list of profiles."""
    import faiss as _faiss

    global _index, _metadata, _loaded
    _loaded = True

    documents = []
    meta_entries = []

    for profile in profiles:
        profile_id = profile.get("id")
        if not profile_id:
            continue

        skill_matrix = profile.get("skill_matrix") or profile.get("skills_json")
        if isinstance(skill_matrix, str):
            try:
                skill_matrix = json.loads(skill_matrix)
            except json.JSONDecodeError:
                skill_matrix = {}

        if not skill_matrix:
            continue

        document = _build_profile_document(skill_matrix)
        raw_text = profile.get("raw_text", "")
        if len(document) < 100 and raw_text:
            document += f"\n\nResume Text:\n{raw_text[:2000]}"

        all_skills: list[str] = []
        skills_data = skill_matrix.get("skills", [])
        if isinstance(skills_data, list):
            for category in skills_data:
                if isinstance(category, dict):
                    for s in category.get("skills", []):
                        if isinstance(s, dict):
                            all_skills.append(s.get("name", "").lower())

        documents.append(document)
        meta_entries.append({
            "profile_id": profile_id,
            "name": skill_matrix.get("name", "Unknown"),
            "email": skill_matrix.get("email", ""),
            "skills_flat": ", ".join(all_skills),
            "document": document,
        })

    if not documents:
        _index = _faiss.IndexFlatIP(EMBEDDING_DIM)
        _metadata = []
        _save_store()
        return 0

    # Batch encode all documents
    model = _get_model()
    logger.info("Encoding %d profiles with %s...", len(documents), MODEL_NAME)
    embeddings = model.encode(documents, normalize_embeddings=True, show_progress_bar=True)

    _index = _faiss.IndexFlatIP(EMBEDDING_DIM)
    _index.add(embeddings.astype(np.float32))
    _metadata = meta_entries

    _save_store()
    logger.info("Rebuilt vector store with %d profiles", len(documents))
    return len(documents)

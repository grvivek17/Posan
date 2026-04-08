import json
from fastapi import APIRouter, Depends
from pydantic import BaseModel
import aiosqlite

from app.database import get_db
from app.ai_helper import call_ai, find_matching_profiles
from app.vector_store import semantic_search

router = APIRouter(prefix="/api/talent-finder", tags=["talent-finder"])


class ChatRequest(BaseModel):
    message: str


@router.post("/chat")
async def chat(request: ChatRequest, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT id, name, email, phone, skills_json FROM profiles")
    rows = await cursor.fetchall()

    profiles_data = []
    for row in rows:
        profile = dict(row)
        if profile.get("skills_json"):
            try:
                profile["skills"] = json.loads(profile["skills_json"])
            except json.JSONDecodeError:
                profile["skills"] = {}
        del profile["skills_json"]
        profiles_data.append(profile)

    if not profiles_data:
        return {
            "response": "No profiles are currently in the system. Please upload some resumes first so I can help you find matching candidates.",
            "matched_profiles": [],
        }

    # Use neural semantic search via FAISS + sentence-transformers
    semantic_results = semantic_search(request.message, n_results=10)

    if semantic_results:
        # True RAG: retrieve relevant profiles, then generate response with LLM
        response = await _rag_response(request.message, semantic_results, profiles_data)
        search_method = "rag"
    else:
        # Fallback to keyword matching if vector store is empty
        response = await find_matching_profiles(request.message, profiles_data)
        search_method = "keyword"

    return {
        "response": response,
        "total_profiles": len(profiles_data),
        "search_method": search_method,
    }


async def _rag_response(query: str, semantic_results: list[dict], profiles_data: list[dict]) -> str:
    """True RAG: retrieve semantically similar profiles, then use LLM to generate a natural response."""
    SIMILARITY_THRESHOLD = 0.15  # Neural embeddings use lower thresholds

    filtered = [r for r in semantic_results if r["similarity"] >= SIMILARITY_THRESHOLD]

    if not filtered:
        return (
            f'No matching profiles found for: "{query}". '
            "The semantic search did not find sufficiently similar profiles. "
            "Try rephrasing your query or upload more resumes with relevant skills."
        )

    # Enrich results with full profile data from DB
    enriched = []
    for result in filtered:
        pid = result["profile_id"]
        db_profile = next((p for p in profiles_data if p["id"] == pid), None)
        if db_profile:
            result["db_profile"] = db_profile
            enriched.append(result)

    if not enriched:
        return (
            f'No matching profiles found for: "{query}". '
            "Profiles were found in the vector store but could not be matched to the database."
        )

    # Build context for LLM from retrieved profiles
    context_parts = []
    for result in enriched:
        pid = result["profile_id"]
        name = result["name"]
        similarity = result["similarity"]
        db_profile = result.get("db_profile", {})
        skills_data = db_profile.get("skills", {})

        # Extract all skills
        all_skills: list[str] = []
        if isinstance(skills_data, dict):
            for cat in skills_data.get("skills", []):
                if isinstance(cat, dict):
                    cat_name = cat.get("category", "")
                    cat_skills = [s.get("name", "") for s in cat.get("skills", []) if isinstance(s, dict)]
                    if cat_name and cat_skills:
                        all_skills.append(f"{cat_name}: {', '.join(cat_skills)}")
        elif isinstance(skills_data, list):
            for cat in skills_data:
                if isinstance(cat, dict):
                    cat_name = cat.get("category", "")
                    cat_skills = [s.get("name", "") for s in cat.get("skills", []) if isinstance(s, dict)]
                    if cat_name and cat_skills:
                        all_skills.append(f"{cat_name}: {', '.join(cat_skills)}")

        email = db_profile.get("email", "")
        phone = db_profile.get("phone", "")

        profile_text = f"Profile #{pid}: {name}"
        if email:
            profile_text += f" ({email})"
        profile_text += f"\nSimilarity Score: {int(similarity * 100)}%"
        if all_skills:
            profile_text += f"\nSkills: {'; '.join(all_skills)}"

        context_parts.append(profile_text)

    context = "\n\n".join(context_parts)

    # Try LLM-powered response generation
    system_prompt = """You are a talent management assistant. You help find the best candidates from a database of profiles.
You will be given a user's query and a list of matching candidate profiles retrieved via semantic search.

Your job is to:
1. Analyze which candidates best match the query
2. Explain WHY each candidate is a good match (mention specific skills)
3. If some candidates are weak matches, say so honestly
4. Use a conversational, helpful tone
5. Format the response with markdown (bold names, bullet points for skills)
6. If the query asks for a team, suggest how the candidates could form a team

Keep the response concise but informative. Do not make up information not in the profiles."""

    user_prompt = f"""User Query: {query}

Retrieved Candidate Profiles (ranked by semantic similarity):
{context}

Based on these profiles, provide a helpful response to the user's query. Explain which candidates match and why."""

    llm_response = await call_ai(system_prompt, user_prompt)

    if not llm_response.startswith("AI_UNAVAILABLE"):
        return llm_response

    # Fallback: format results without LLM
    return _format_results_fallback(query, enriched)


def _format_results_fallback(query: str, enriched: list[dict]) -> str:
    """Format search results without LLM (fallback)."""
    response_lines = [
        f'Found {len(enriched)} matching profile(s) for: "{query}" (neural semantic search)\n'
    ]

    for i, result in enumerate(enriched, 1):
        name = result["name"]
        similarity = result["similarity"]
        pid = result["profile_id"]

        db_profile = result.get("db_profile", {})
        skills_data = db_profile.get("skills", {})
        top_skills: list[str] = []
        if isinstance(skills_data, dict):
            for cat in skills_data.get("skills", []):
                if isinstance(cat, dict):
                    for s in cat.get("skills", []):
                        if isinstance(s, dict):
                            top_skills.append(s.get("name", ""))
        elif isinstance(skills_data, list):
            for cat in skills_data:
                if isinstance(cat, dict):
                    for s in cat.get("skills", []):
                        if isinstance(s, dict):
                            top_skills.append(s.get("name", ""))

        if similarity >= 0.6:
            relevance = "Excellent match"
        elif similarity >= 0.45:
            relevance = "Strong match"
        elif similarity >= 0.35:
            relevance = "Good match"
        elif similarity >= 0.25:
            relevance = "Moderate match"
        else:
            relevance = "Possible match"

        pct = int(similarity * 100)
        response_lines.append(f"{i}. **{name}** (Profile #{pid})")
        response_lines.append(f"   Relevance: {relevance} ({pct}% similarity)")
        if top_skills:
            response_lines.append(f"   Key skills: {', '.join(top_skills[:10])}")
        response_lines.append("")

    return "\n".join(response_lines)

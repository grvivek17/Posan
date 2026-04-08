import os
import json
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from PyPDF2 import PdfReader
from docx import Document
import io
import aiosqlite

from app.database import get_db
from app.ai_helper import generate_skill_matrix
from app.vector_store import add_profile_to_vector_store, remove_profile_from_vector_store, rebuild_vector_store_from_profiles

router = APIRouter(prefix="/api/profiles", tags=["profiles"])

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def extract_text_from_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"
    return text.strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    doc = Document(io.BytesIO(file_bytes))
    text = "\n".join([para.text for para in doc.paragraphs if para.text.strip()])
    return text.strip()


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...), db: aiosqlite.Connection = Depends(get_db)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file provided")

    ext = file.filename.rsplit(".", 1)[-1].lower() if "." in file.filename else ""
    if ext not in ("pdf", "doc", "docx"):
        raise HTTPException(status_code=400, detail="Only PDF and DOC/DOCX files are supported")

    file_bytes = await file.read()

    # Save file
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        f.write(file_bytes)

    # Extract text
    if ext == "pdf":
        raw_text = extract_text_from_pdf(file_bytes)
    elif ext in ("doc", "docx"):
        raw_text = extract_text_from_docx(file_bytes)
    else:
        raw_text = ""

    if not raw_text:
        raise HTTPException(status_code=400, detail="Could not extract text from the uploaded file")

    # Generate skill matrix via AI
    skill_matrix = await generate_skill_matrix(raw_text)

    name = skill_matrix.get("name", file.filename)
    email = skill_matrix.get("email", "")
    phone = skill_matrix.get("phone", "")

    cursor = await db.execute(
        """INSERT INTO profiles (name, email, phone, filename, raw_text, skills_json)
           VALUES (?, ?, ?, ?, ?, ?)""",
        (name, email, phone, file.filename, raw_text, json.dumps(skill_matrix))
    )
    await db.commit()
    profile_id = cursor.lastrowid

    # Add to vector store for semantic search
    add_profile_to_vector_store(profile_id, skill_matrix, raw_text)

    return {
        "id": profile_id,
        "name": name,
        "email": email,
        "phone": phone,
        "filename": file.filename,
        "skill_matrix": skill_matrix,
    }


@router.get("/")
async def list_profiles(db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM profiles ORDER BY created_at DESC")
    rows = await cursor.fetchall()
    profiles = []
    for row in rows:
        profile = dict(row)
        if profile.get("skills_json"):
            try:
                profile["skill_matrix"] = json.loads(profile["skills_json"])
            except json.JSONDecodeError:
                profile["skill_matrix"] = {}
        else:
            profile["skill_matrix"] = {}
        profiles.append(profile)
    return profiles


@router.post("/rebuild-index")
async def rebuild_index(db: aiosqlite.Connection = Depends(get_db)):
    """Rebuild the ChromaDB vector index from all existing profiles."""
    cursor = await db.execute("SELECT id, raw_text, skills_json FROM profiles")
    rows = await cursor.fetchall()
    profiles_list = []
    for row in rows:
        profile = dict(row)
        profiles_list.append(profile)
    count = rebuild_vector_store_from_profiles(profiles_list)
    return {"message": f"Rebuilt vector index with {count} profiles", "indexed": count}


@router.get("/{profile_id}")
async def get_profile(profile_id: int, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT * FROM profiles WHERE id = ?", (profile_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")
    profile = dict(row)
    if profile.get("skills_json"):
        try:
            profile["skill_matrix"] = json.loads(profile["skills_json"])
        except json.JSONDecodeError:
            profile["skill_matrix"] = {}
    return profile


@router.delete("/{profile_id}")
async def delete_profile(profile_id: int, db: aiosqlite.Connection = Depends(get_db)):
    cursor = await db.execute("SELECT filename FROM profiles WHERE id = ?", (profile_id,))
    row = await cursor.fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Profile not found")

    # Remove file
    file_path = os.path.join(UPLOAD_DIR, row["filename"])
    if os.path.exists(file_path):
        os.remove(file_path)

    await db.execute("DELETE FROM profiles WHERE id = ?", (profile_id,))
    await db.commit()

    # Remove from vector store
    remove_profile_from_vector_store(profile_id)

    return {"message": "Profile deleted"}

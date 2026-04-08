import aiosqlite
import os

DATABASE_PATH = os.getenv("DATABASE_PATH", "talent.db")


async def get_db():
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    try:
        yield db
    finally:
        await db.close()


async def init_db():
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS profiles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                filename TEXT NOT NULL,
                raw_text TEXT,
                skills_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS requirements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                skills_needed TEXT,
                team_size INTEGER DEFAULT 1,
                status TEXT DEFAULT 'open',
                matched_profiles TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS telecaller_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                requirement_id INTEGER,
                question TEXT NOT NULL,
                question_order INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (requirement_id) REFERENCES requirements(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS telecaller_calls (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                profile_id INTEGER NOT NULL,
                requirement_id INTEGER,
                status TEXT DEFAULT 'pending',
                call_notes TEXT,
                twilio_sid TEXT,
                twilio_status TEXT,
                call_duration INTEGER,
                recording_url TEXT,
                phone_number TEXT,
                questions_json TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (profile_id) REFERENCES profiles(id),
                FOREIGN KEY (requirement_id) REFERENCES requirements(id)
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS telecaller_responses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                call_id INTEGER NOT NULL,
                question_id INTEGER NOT NULL,
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (call_id) REFERENCES telecaller_calls(id),
                FOREIGN KEY (question_id) REFERENCES telecaller_questions(id)
            )
        """)
        # Add req_code column to requirements table if missing
        try:
            await db.execute("ALTER TABLE requirements ADD COLUMN req_code TEXT")
        except Exception:
            pass
        # Backfill req_code for existing requirements that don't have one
        cursor = await db.execute(
            "SELECT id FROM requirements WHERE req_code IS NULL ORDER BY id"
        )
        rows_without_code = await cursor.fetchall()
        if rows_without_code:
            count_cursor = await db.execute(
                "SELECT COUNT(*) FROM requirements WHERE req_code IS NOT NULL"
            )
            count_row = await count_cursor.fetchone()
            start = (count_row[0] if count_row else 0) + 1
            for i, row in enumerate(rows_without_code):
                code = f"REQ-{start + i:03d}"
                await db.execute(
                    "UPDATE requirements SET req_code = ? WHERE id = ?",
                    (code, row[0])
                )
        # Add Twilio columns to existing telecaller_calls table if missing
        try:
            await db.execute("ALTER TABLE telecaller_calls ADD COLUMN twilio_sid TEXT")
        except Exception:
            pass
        try:
            await db.execute("ALTER TABLE telecaller_calls ADD COLUMN twilio_status TEXT")
        except Exception:
            pass
        try:
            await db.execute("ALTER TABLE telecaller_calls ADD COLUMN call_duration INTEGER")
        except Exception:
            pass
        try:
            await db.execute("ALTER TABLE telecaller_calls ADD COLUMN recording_url TEXT")
        except Exception:
            pass
        try:
            await db.execute("ALTER TABLE telecaller_calls ADD COLUMN phone_number TEXT")
        except Exception:
            pass
        try:
            await db.execute("ALTER TABLE telecaller_calls ADD COLUMN questions_json TEXT")
        except Exception:
            pass
        await db.commit()

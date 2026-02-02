from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# Try Supabase first, fall back to SQLite if connection fails
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/qrcode_db")

# For now, use SQLite for local testing due to Supabase connectivity issues
# TODO: Switch back to Supabase once connection is resolved
USE_SQLITE = os.getenv("USE_SQLITE", "true").lower() == "true"

if USE_SQLITE:
    # SQLite for local development
    SQLITE_URL = "sqlite:///./qrcode.db"
    engine = create_engine(SQLITE_URL, connect_args={"check_same_thread": False})
    print(f"🗄️  Using SQLite database: {SQLITE_URL}")
else:
    # Supabase/PostgreSQL
    engine = create_engine(DATABASE_URL)
    print(f"🗄️  Using PostgreSQL database")
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Dependency to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

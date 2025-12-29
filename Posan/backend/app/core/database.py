from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from app.core.config import settings

# Ensure the database URL uses the correct dialect for psycopg2
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg2://", 1)

# Create database engine
# Optimized for serverless (Vercel) - smaller pool sizes
engine = create_engine(
    database_url,
    pool_pre_ping=True,  # Verify connections before using
    pool_size=1,         # Small pool for serverless
    max_overflow=2,      # Limited overflow for serverless
    pool_recycle=300     # Recycle connections every 5 minutes
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models using SQLAlchemy 2.0 style
class Base(DeclarativeBase):
    # Prevent Pydantic from trying to validate SQLAlchemy models
    __allow_unmapped__ = True


def get_db():
    """
    Dependency function to get database session.
    Yields a database session and closes it after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

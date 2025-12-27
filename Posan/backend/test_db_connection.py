import sys
sys.path.insert(0, '.')

from app.core.config import settings
from sqlalchemy import create_engine, text

print("Testing Neon DB connection...")
print(f"Database URL: {settings.DATABASE_URL[:50]}...")

# Prepare the URL for psycopg
database_url = settings.DATABASE_URL
if database_url.startswith("postgresql://"):
    database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

print(f"Using dialect: postgresql+psycopg")

try:
    # Create engine
    engine = create_engine(database_url, pool_pre_ping=True)
    
    # Test connection
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"✅ Successfully connected to PostgreSQL!")
        print(f"Version: {version[:80]}...")
        
        # Test creating a simple table
        conn.execute(text("CREATE TABLE IF NOT EXISTS test_table (id SERIAL PRIMARY KEY, name VARCHAR(50))"))
        conn.execute(text("INSERT INTO test_table (name) VALUES ('test') ON CONFLICT DO NOTHING"))
        conn.commit()
        print("✅ Successfully created test table and inserted data!")
        
        # Clean up
        conn.execute(text("DROP TABLE IF EXISTS test_table"))
        conn.commit()
        print("✅ Test table cleaned up!")
        
except Exception as e:
    print(f"❌ Connection failed: {type(e).__name__}: {str(e)}")
    import traceback
    traceback.print_exc()

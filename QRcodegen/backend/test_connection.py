"""
Simple test script to verify Supabase database connection
"""
from sqlalchemy import create_engine, text
import os

print("=" * 60)
print("Testing Supabase Database Connection")
print("=" * 60)
print()

# Try to read .env file manually
env_file = ".env"
DATABASE_URL = None

if os.path.exists(env_file):
    print("Found .env file")
    with open(env_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line.startswith('DATABASE_URL'):
                # Extract DATABASE_URL
                DATABASE_URL = line.split('=', 1)[1].strip()
                break

if not DATABASE_URL:
    print("ERROR: DATABASE_URL not found in .env file")
    exit(1)

# Hide password in output
if "@" in DATABASE_URL:
    parts = DATABASE_URL.split("@")
    masked = f"postgresql://postgres:****@{parts[1]}"
    print(f"Connection: {masked}")
else:
    print(f"Connection: {DATABASE_URL[:30]}...")

print()
print("Attempting to connect...")
print()

try:
    # Create engine
    engine = create_engine(DATABASE_URL)
    
    # Test connection
    with engine.connect() as connection:
        # Execute a simple query
        result = connection.execute(text("SELECT version();"))
        version = result.fetchone()[0]
        
        print("SUCCESS! Connected to Supabase database")
        print()
        print(f"PostgreSQL Version:")
        print(f"   {version[:80]}...")
        print()
        
        # Check if our table exists
        result = connection.execute(text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'qrcodes'
            );
        """))
        table_exists = result.fetchone()[0]
        
        if table_exists:
            print("Table 'qrcodes' already exists")
            
            # Count records
            result = connection.execute(text("SELECT COUNT(*) FROM qrcodes;"))
            count = result.fetchone()[0]
            print(f"Current QR codes in database: {count}")
        else:
            print("Table 'qrcodes' does not exist yet")
            print("It will be created automatically when you start the FastAPI server")
        
        print()
        print("=" * 60)
        print("Database connection test PASSED!")
        print("=" * 60)
        print()
        print("Next steps:")
        print("1. Start backend: uvicorn app.main:app --reload")
        print("2. Start frontend: cd ../frontend && npm run dev")
        print("3. Open http://localhost:3000")
        
except Exception as e:
    print("ERROR: Failed to connect to database")
    print()
    print(f"Error: {str(e)}")
    print()
    print("Troubleshooting:")
    print("1. Check your password in backend/.env file")
    print("2. Make sure you replaced [YOUR-PASSWORD] with actual password")
    print("3. Verify your Supabase project is active")
    print("4. Check your internet connection")
    print()
    exit(1)

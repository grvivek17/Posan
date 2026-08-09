import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("No DATABASE_URL found in .env")
    exit(1)

engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    try:
        print("Adding keycloak_id column to users table...")
        # Check if the column exists first
        result = conn.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='users' and column_name='keycloak_id';
        """)).fetchone()
        
        if not result:
            conn.execute(text("ALTER TABLE users ADD COLUMN keycloak_id VARCHAR UNIQUE;"))
            conn.execute(text("CREATE INDEX ix_users_keycloak_id ON users (keycloak_id);"))
            print("Successfully added keycloak_id column and index.")
        else:
            print("keycloak_id column already exists.")
            
        # Also need to make hashed_password nullable
        print("Making hashed_password nullable...")
        conn.execute(text("ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL;"))
        print("Successfully made hashed_password nullable.")
        
        conn.commit()
    except Exception as e:
        print(f"Error migrating database: {e}")

import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'posan.db')

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # Check if keycloak_id column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'keycloak_id' not in columns:
            print("Adding keycloak_id column to users table...")
            cursor.execute("ALTER TABLE users ADD COLUMN keycloak_id VARCHAR DEFAULT NULL")
            cursor.execute("CREATE UNIQUE INDEX ix_users_keycloak_id ON users (keycloak_id)")
            print("Successfully added keycloak_id column.")
        else:
            print("keycloak_id column already exists.")
            
        # Optional: Make hashed_password nullable (SQLite doesn't easily support ALTER COLUMN)
        # We can just leave it as is, since our ORM handles it, and if it's already created with NOT NULL,
        # we might have issues with JIT provisioning if we don't provide a dummy hash.
        # But wait, JIT provisioning explicitly sets it to None. 
        # In SQLite, if it was created as NOT NULL, inserting None will fail.
        # Let's check the users table definition:
        
    except sqlite3.Error as e:
        print(f"SQLite error: {e}")
    finally:
        conn.commit()
        conn.close()

if __name__ == "__main__":
    migrate()

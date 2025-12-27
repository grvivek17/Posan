import psycopg

# Direct connection string
conn_string = "postgresql://neondb_owner:npg_NnJ5sICAUpa7@ep-empty-cake-a4z84d12-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

print("Testing direct psycopg connection...")

try:
    with psycopg.connect(conn_string) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT version()")
            version = cur.fetchone()[0]
            print(f"✅ Connected successfully!")
            print(f"PostgreSQL version: {version[:100]}")
            
            # Test table creation
            cur.execute("CREATE TABLE IF NOT EXISTS test_posan (id SERIAL PRIMARY KEY, name VARCHAR(50))")
            conn.commit()
            print("✅ Test table created!")
            
            # Clean up
            cur.execute("DROP TABLE IF EXISTS test_posan")
            conn.commit()
            print("✅ Test complete!")
            
except Exception as e:
    print(f"❌ Connection failed: {e}")
    import traceback
    traceback.print_exc()

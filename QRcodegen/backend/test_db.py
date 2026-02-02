import os
import socket

print("="*60)
print("SUPABASE CONNECTION DIAGNOSTIC")
print("="*60)

# Read .env
print("\n1. Reading .env file...")
with open('.env', 'r', encoding='utf-8') as f:
    content = f.read()
    for line in content.split('\n'):
        line = line.strip()
        if line.startswith('DATABASE_URL'):
            DATABASE_URL = line.split('=', 1)[1].strip()
            
            # Parse the URL
            if '@' in DATABASE_URL:
                parts = DATABASE_URL.split('@')
                host_port_db = parts[1]
                host = host_port_db.split(':')[0]
                port = int(host_port_db.split(':')[1].split('/')[0])
                
                print(f"   ✓ Found DATABASE_URL")
                print(f"   Host: {host}")
                print(f"   Port: {port}")
            break

# Test DNS resolution
print("\n2. Testing DNS resolution...")
try:
    ip = socket.gethostbyname(host)
    print(f"   ✓ DNS resolved: {host} -> {ip}")
except Exception as e:
    print(f"   ✗ DNS resolution failed: {e}")
    print("   Check your internet connection")
    exit(1)

# Test network connectivity
print(f"\n3. Testing network connectivity to {host}:{port}...")
try:
    sock = socket.create_connection((host, port), timeout=10)
    sock.close()
    print(f"   ✓ Port {port} is reachable")
except Exception as e:
    print(f"   ✗ Cannot reach {host}:{port}")
    print(f"   Error: {e}")
    print("\n   Possible issues:")
    print("   - Firewall blocking connection")
    print("   - Supabase project is paused/inactive")
    print("   - Network connectivity issue")
    exit(1)

# Test database connection
print("\n4. Testing PostgreSQL connection...")
try:
    from sqlalchemy import create_engine, text
    engine = create_engine(DATABASE_URL, connect_args={"connect_timeout": 10})
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        version = result.fetchone()[0]
        print(f"   ✓ Connected successfully!")
        print(f"   PostgreSQL: {version[:60]}...")
        
    print("\n" + "="*60)
    print("✓ ALL TESTS PASSED!")
    print("="*60)
    print("\nYour Supabase database is ready!")
    print("\nNext: Start the backend server:")
    print("  uvicorn app.main:app --reload")
    
except Exception as e:
    print(f"   ✗ Database connection failed")
    print(f"   Error: {e}")
    print("\n   Possible issues:")
    print("   - Wrong password in .env file")
    print("   - Database name incorrect")
    print("   - SSL certificate issue")
    import traceback
    traceback.print_exc()
    exit(1)

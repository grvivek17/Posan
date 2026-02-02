from app.core.database import engine
from sqlalchemy import text

print("=== Checking Users and Subscriptions ===\n")

conn = engine.connect()

# Check users
print("Users:")
result = conn.execute(text("SELECT id, username, email FROM users LIMIT 5"))
users = result.fetchall()
for row in users:
    print(f"  ID: {row[0]}, Username: {row[1]}, Email: {row[2]}")

print("\n" + "="*50 + "\n")

# Check subscriptions
print("Subscriptions:")
result = conn.execute(text("""
    SELECT s.id, s.user_id, u.username, s.tier, s.status, s.expires_at 
    FROM subscriptions s 
    JOIN users u ON s.user_id = u.id
"""))
subs = result.fetchall()

if not subs:
    print("  No subscriptions found!")
else:
    for row in subs:
        print(f"  User: {row[2]} (ID: {row[1]}) - Tier: {row[3]}, Status: {row[4]}, Expires: {row[5]}")

conn.close()

print("\n" + "="*50)
print("To upgrade a user to Pro, run:")
print("  python upgrade_user_to_pro.py <username>")

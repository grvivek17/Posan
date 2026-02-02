"""
Quick test script to check upgrade endpoint
Run this to see the actual error
"""
import requests
import json

# Get token from your browser localStorage
# Run this in browser console: localStorage.getItem('token')
TOKEN = "YOUR_TOKEN_HERE"  # Replace with actual token

API_BASE = "http://localhost:8000/api/v1"

def test_upgrade():
    print("=" * 60)
    print("Testing Subscription Upgrade Endpoint")
    print("=" * 60)
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {TOKEN}"
    }
    
    data = {
        "tier": "pro",
        "payment_provider": "test",
        "payment_id": f"test_script_{123456}"
    }
    
    print(f"\n📤 Sending POST request to {API_BASE}/subscription/upgrade")
    print(f"📦 Data: {json.dumps(data, indent=2)}")
    print(f"🔑 Token: {TOKEN[:20]}...")
    print()
    
    try:
        response = requests.post(
            f"{API_BASE}/subscription/upgrade",
            headers=headers,
            json=data
        )
        
        print(f"📊 Status Code: {response.status_code}")
        print(f"📄 Response:")
        print(json.dumps(response.json(), indent=2))
        
        if response.status_code == 200:
            print("\n✅ SUCCESS! Upgrade worked!")
        else:
            print(f"\n❌ FAILED with status {response.status_code}")
            print("Error details above ⬆️")
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")

if __name__ == "__main__":
    if TOKEN == "YOUR_TOKEN_HERE":
        print("❌ Please update TOKEN in the script!")
        print("\nTo get your token:")
        print("1. Open browser (with app loaded)")
        print("2. Press F12 for console")
        print("3. Run: localStorage.getItem('token')")
        print("4. Copy the token")
        print("5. Paste it in this script")
    else:
        test_upgrade()

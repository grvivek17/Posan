"""
Test script to verify password reset functionality
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1/auth"

def test_password_reset():
    print("=" * 60)
    print("PASSWORD RESET TEST")
    print("=" * 60)
    
    # Step 1: Request password reset
    email = "test@example.com"  # Replace with your test email
    print(f"\n1. Requesting password reset for: {email}")
    
    response = requests.post(
        f"{BASE_URL}/forgot-password",
        params={"email": email}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code != 200:
        print("❌ Failed to request password reset")
        return
    
    data = response.json()
    if not data.get("reset_token"):
        print("❌ No reset token received")
        return
    
    token = data["reset_token"]
    print(f"\n✅ Reset token received: {token[:50]}...")
    
    # Step 2: Verify token
    print(f"\n2. Verifying reset token...")
    
    response = requests.post(
        f"{BASE_URL}/verify-reset-token",
        params={"token": token}
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if not response.json().get("valid"):
        print("❌ Token is not valid")
        return
    
    print(f"✅ Token is valid for: {response.json().get('email')}")
    
    # Step 3: Reset password
    new_password = "newpassword123"
    print(f"\n3. Resetting password to: {new_password}")
    
    response = requests.post(
        f"{BASE_URL}/reset-password",
        params={
            "token": token,
            "new_password": new_password
        }
    )
    
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code != 200:
        print("❌ Failed to reset password")
        return
    
    print(f"\n✅ Password reset successful!")
    
    # Step 4: Try to login with new password
    print(f"\n4. Testing login with new password...")
    
    response = requests.post(
        f"{BASE_URL}/login",
        json={
            "username": email.split("@")[0],  # Assuming username is email prefix
            "password": new_password
        }
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        print("✅ Login successful with new password!")
        print(f"Access token received: {response.json().get('access_token')[:50]}...")
    else:
        print(f"❌ Login failed: {response.json()}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_password_reset()

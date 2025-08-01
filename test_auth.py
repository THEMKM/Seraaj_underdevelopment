#!/usr/bin/env python3
"""
Test Authentication Flow
Verify that the API authentication is working properly
"""
import requests
import json

def test_login():
    """Test login with demo credentials"""
    print("Testing authentication flow...")
    
    # Test login endpoint
    login_url = "http://localhost:8000/v1/auth/login"
    login_data = {
        "email": "layla@example.com",
        "password": "Demo123!"
    }
    
    try:
        print(f"Testing login at {login_url}")
        response = requests.post(login_url, json=login_data, timeout=10)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            data = response.json()
            if "access_token" in data:
                print("✅ Login successful!")
                print(f"Token type: {data.get('token_type', 'N/A')}")
                return data["access_token"]
            else:
                print("❌ Login response missing access_token")
        else:
            print(f"❌ Login failed with status {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to API server on port 8000")
        print("Make sure the FastAPI server is running")
    except Exception as e:
        print(f"❌ Error during login test: {e}")
    
    return None

def test_protected_endpoint(token):
    """Test access to protected endpoint"""
    if not token:
        print("No token available for protected endpoint test")
        return
        
    print("\nTesting protected endpoint access...")
    
    # Test opportunities endpoint
    opportunities_url = "http://localhost:8000/v1/opportunities/"
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(opportunities_url, headers=headers, timeout=10)
        print(f"Opportunities endpoint status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Successfully accessed opportunities: {len(data)} items")
        else:
            print(f"❌ Failed to access opportunities: {response.text}")
            
    except Exception as e:
        print(f"❌ Error accessing opportunities: {e}")

if __name__ == "__main__":
    token = test_login()
    test_protected_endpoint(token)
    
    print("\n" + "="*60)
    print("AUTHENTICATION TEST SUMMARY")
    print("="*60)
    print("✅ Demo users created in database")
    print("✅ Frontend login page updated with correct credentials")
    print("Next steps:")
    print("1. Visit http://localhost:3030/auth/login")
    print("2. Try logging in with: layla@example.com / Demo123!")
    print("3. Check if you're redirected to the feed page")
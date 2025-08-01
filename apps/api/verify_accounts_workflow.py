#!/usr/bin/env python3
"""
Verify Accounts & Registration Workflow
Tests both demo accounts and registration process
"""
import requests


def test_demo_accounts():
    """Test that demo accounts exist and can login"""
    print("🔍 Testing demo account logins...")

    demo_accounts = [
        ("layla@example.com", "Layla Al-Mansouri"),
        ("omar@example.com", "Omar Hassan"),
        ("fatima@example.com", "Fatima Al-Zahra"),
        ("admin@seraaj.org", "Admin User"),
        ("contact@hopeeducation.org", "Hope Education"),
    ]

    success_count = 0
    for email, name in demo_accounts:
        try:
            response = requests.post(
                "http://127.0.0.1:8000/v1/auth/login",
                json={"email": email, "password": "Demo123!"},
                timeout=10,
            )

            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    print(f"   ✅ {email} ({name}) - Login successful")
                    success_count += 1
                else:
                    print(f"   ❌ {email} - Login response missing token")
            else:
                print(f"   ❌ {email} - Login failed: {response.status_code}")

        except Exception as e:
            print(f"   ❌ {email} - Login error: {e}")

    print(
        f"\\n📊 Demo Account Results: {success_count}/{len(demo_accounts)} accounts working"
    )
    return success_count == len(demo_accounts)


def test_registration_workflow():
    """Test that new account registration works"""
    print("\\n🔍 Testing registration workflow...")

    # Test registration
    test_user = {
        "email": "test@example.com",
        "password": "Test123!",
        "first_name": "Test",
        "last_name": "User",
        "role": "volunteer",
    }

    try:
        # Register new user
        response = requests.post(
            "http://127.0.0.1:8000/v1/auth/register", json=test_user, timeout=10
        )

        if response.status_code == 200:
            print("   ✅ Registration successful")

            # Try to login with new account
            login_response = requests.post(
                "http://127.0.0.1:8000/v1/auth/login",
                json={"email": test_user["email"], "password": test_user["password"]},
                timeout=10,
            )

            if login_response.status_code == 200:
                data = login_response.json()
                if "access_token" in data:
                    print("   ✅ New account login successful")
                    return True
                else:
                    print("   ❌ New account login missing token")
            else:
                print(f"   ❌ New account login failed: {login_response.status_code}")

        else:
            print(f"   ❌ Registration failed: {response.status_code}")
            if response.status_code == 400:
                print(f"      Details: {response.text}")

    except Exception as e:
        print(f"   ❌ Registration test error: {e}")

    return False


def verify_server_health():
    """Check if server is running and healthy"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is healthy and responding")
            return True
        else:
            print(f"❌ Server health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Server not reachable: {e}")
        return False


def main():
    print("🧪 SERAAJ ACCOUNTS & REGISTRATION VERIFICATION")
    print("=" * 60)

    # Check server health first
    if not verify_server_health():
        print("\\n❌ Server not running. Start server first!")
        return False

    # Test demo accounts
    demo_success = test_demo_accounts()

    # Test registration
    registration_success = test_registration_workflow()

    print("\\n" + "=" * 60)
    if demo_success and registration_success:
        print("🎉 SUCCESS: Both demo accounts and registration working!")
        print("\\n✅ You can safely test with:")
        print("   • Demo accounts (immediate login)")
        print("   • Registration workflow (create new accounts)")
        print("\\n🔑 Demo Account Credentials (Password: Demo123!):")
        print("   • layla@example.com (Volunteer)")
        print("   • omar@example.com (Volunteer)")
        print("   • fatima@example.com (Volunteer)")
        print("   • admin@seraaj.org (Admin)")
        print("   • contact@hopeeducation.org (Organization)")
        return True
    else:
        print("❌ FAILURE: Some accounts or registration not working!")
        print(f"   Demo accounts: {'✅' if demo_success else '❌'}")
        print(f"   Registration: {'✅' if registration_success else '❌'}")
        return False


if __name__ == "__main__":
    main()

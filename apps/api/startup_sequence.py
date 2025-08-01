#!/usr/bin/env python3
"""
Complete Startup Sequence for Seraaj Platform
Ensures demo accounts exist and registration works
"""
import subprocess
import time
import requests
import sys
import os

def wait_for_server(max_wait=30):
    """Wait for server to be ready"""
    print("⏳ Waiting for server to start...")
    
    for i in range(max_wait):
        try:
            response = requests.get("http://127.0.0.1:8000/health", timeout=2)
            if response.status_code == 200:
                print(f"✅ Server ready after {i+1} seconds")
                return True
        except:
            pass
        time.sleep(1)
        if i % 5 == 4:  # Print progress every 5 seconds
            print(f"   Still waiting... ({i+1}/{max_wait}s)")
    
    print("❌ Server failed to start within 30 seconds")
    return False

def create_demo_accounts():
    """Run the demo account creation script"""
    print("\\n👥 Creating demo accounts...")
    
    try:
        result = subprocess.run([
            sys.executable, "create_minimal_demo.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        if result.returncode == 0:
            print("✅ Demo accounts created successfully")
            print(result.stdout)
            return True
        else:
            print("❌ Demo account creation failed")
            print("STDOUT:", result.stdout)
            print("STDERR:", result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error running demo script: {e}")
        return False

def verify_everything():
    """Run the verification script"""
    print("\\n🧪 Verifying accounts and registration...")
    
    try:
        result = subprocess.run([
            sys.executable, "verify_accounts_workflow.py"
        ], capture_output=True, text=True, cwd=os.getcwd())
        
        print(result.stdout)
        if result.stderr:
            print("STDERR:", result.stderr)
            
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error running verification: {e}")
        return False

def main():
    print("🚀 SERAAJ PLATFORM STARTUP SEQUENCE")
    print("="*50)
    print("This will:")
    print("1. Wait for server to be ready")
    print("2. Create demo accounts")
    print("3. Verify login and registration work")
    print("="*50)
    
    # Wait for server
    if not wait_for_server():
        print("\\n❌ FAILED: Server not starting")
        print("Manual steps needed:")
        print("1. Check server logs for errors")
        print("2. Fix any import/model issues")
        print("3. Restart server manually")
        return False
    
    # Create demo accounts
    if not create_demo_accounts():
        print("\\n❌ FAILED: Demo accounts not created")
        print("Manual steps needed:")
        print("1. Check database schema issues")
        print("2. Run create_minimal_demo.py manually")
        return False
    
    # Verify everything works
    if not verify_everything():
        print("\\n❌ FAILED: Verification failed")
        print("Manual testing needed:")
        print("1. Try logging in manually") 
        print("2. Check registration endpoint")
        return False
    
    print("\\n🎉 SUCCESS: Platform ready for testing!")
    print("\\nYou can now:")
    print("• Login with demo accounts immediately")
    print("• Test registration by creating new accounts")
    print("• Go crazy testing all functionality!")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
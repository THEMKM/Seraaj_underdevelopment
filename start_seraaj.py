#!/usr/bin/env python3
"""
Seraaj Platform Startup Script
Starts both backend and frontend servers
"""
import os
import sys
import subprocess
import time
import requests

def start_backend():
    """Start the FastAPI backend server"""
    print("Starting backend server...")
    backend_dir = r"C:\Users\Mohamad\Documents\Claude\Seraaj\apps\api"
    
    # Start backend in a new process
    backend_cmd = [
        sys.executable, "-m", "uvicorn", "main:app", 
        "--host", "127.0.0.1", "--port", "8000", "--reload"
    ]
    
    backend_process = subprocess.Popen(
        backend_cmd, 
        cwd=backend_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    
    # Wait for backend to start
    print("Waiting for backend to start...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:8000/health", timeout=2)
            if response.status_code == 200:
                print("Backend server started successfully on http://localhost:8000")
                return backend_process
        except:
            pass
        time.sleep(1)
    
    print("Backend server may not have started properly")
    return backend_process

def start_frontend():
    """Start the Next.js frontend server"""
    print("Starting frontend server...")
    frontend_dir = r"C:\Users\Mohamad\Documents\Claude\Seraaj\apps\web"
    
    # Start frontend in a new process
    frontend_cmd = ["npm", "run", "dev"]
    
    frontend_process = subprocess.Popen(
        frontend_cmd,
        cwd=frontend_dir,
        creationflags=subprocess.CREATE_NEW_CONSOLE
    )
    
    # Wait for frontend to start
    print("Waiting for frontend to start...")
    for i in range(30):  # Wait up to 30 seconds
        try:
            response = requests.get("http://localhost:3030", timeout=2)
            if response.status_code == 200:
                print("Frontend server started successfully on http://localhost:3030")
                return frontend_process
        except:
            pass
        time.sleep(1)
    
    print("Frontend server may not have started properly")
    return frontend_process

def main():
    print("=" * 60)
    print("SERAAJ PLATFORM STARTUP")
    print("=" * 60)
    
    # Start both servers
    backend_process = start_backend()
    frontend_process = start_frontend()
    
    print("\n" + "=" * 60)
    print("STARTUP COMPLETE!")
    print("=" * 60)
    print("Backend API: http://localhost:8000")
    print("  - Health check: http://localhost:8000/health")
    print("  - API docs: http://localhost:8000/docs")
    print("  - Search opportunities: http://localhost:8000/v1/opportunities/search")
    print("")
    print("Frontend App: http://localhost:3030")
    print("  - Main website: http://localhost:3030")
    print("  - Login page: http://localhost:3030/auth/login")
    print("")
    print("Demo accounts (password: Demo123!):")
    print("  - layla@example.com (Volunteer)")
    print("  - omar@example.com (Volunteer)")
    print("  - contact@hopeeducation.org (Organization)")
    print("")
    print("Both servers are running in separate console windows.")
    print("Close those console windows to stop the servers.")
    print("=" * 60)

if __name__ == "__main__":
    main()
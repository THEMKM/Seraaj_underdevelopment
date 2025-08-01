#!/usr/bin/env python3
"""
Simple server startup script for testing
"""
import uvicorn
from main import app

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 STARTING SERAAJ API SERVER")
    print("=" * 60)
    print("Server will be available at:")
    print("  • http://localhost:8000")
    print("  • http://127.0.0.1:8000")
    print("")
    print("Available endpoints:")
    print("  • Health check: http://localhost:8000/health")
    print("  • API docs: http://localhost:8000/docs")
    print("  • Search opportunities: http://localhost:8000/v1/opportunities/search")
    print("  • List opportunities: http://localhost:8000/v1/opportunities/")
    print("")
    print("Demo accounts (password: Demo123!):")
    print("  • layla@example.com (Volunteer)")
    print("  • omar@example.com (Volunteer)")
    print("  • contact@hopeeducation.org (Organization)")
    print("")
    print("=" * 60)
    print("Starting server...")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        reload=False,
        log_level="info"
    )
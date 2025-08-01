#!/usr/bin/env python3
"""
Simple test server with just opportunities router
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import create_db_and_tables
from routers import opportunities, auth

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    # Startup logic
    create_db_and_tables()
    print("Database initialized")
    
    yield
    
    # Shutdown logic (if needed)
    pass


# Create FastAPI app
app = FastAPI(title="Simple Seraaj API Test", lifespan=lifespan)

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(opportunities.router)


@app.get("/")
async def root():
    return {"message": "Simple Seraaj API Test Server"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8002)
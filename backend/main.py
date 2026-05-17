"""
Court in Your Pocket - Backend API
FastAPI application with IBM watsonx integration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from routers import chat


import os
from dotenv import load_dotenv

# Import routers
from session import session
from routers.legal import router as legal_router

# Import utilities
from session import session_store

# Load environment variables
load_dotenv()

# Configuration
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    print("[STARTUP] Starting Court in Your Pocket API...")
    print(f"[STARTUP] Frontend URL: {FRONTEND_URL}")
    print(f"[STARTUP] Backend Port: {BACKEND_PORT}")
    
    # Cleanup expired sessions on startup
    cleaned = session_store.cleanup_expired_sessions()
    print(f"[STARTUP] Cleaned up {cleaned} expired sessions")
    
    yield
    
    # Shutdown
    print("[SHUTDOWN] Court in Your Pocket API shutting down...")


# Initialize FastAPI app
app = FastAPI(
    title="Court in Your Pocket API",
    description="AI-powered legal assistance for Indian citizens",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(session.router)
app.include_router(legal_router)
app.include_router(chat.router)

# Root endpoint
@app.get("/", tags=["health"])
def root():
    """
    Root endpoint - API health check.
    """
    return {
        "message": "Welcome to Court in Your Pocket API",
        "status": "healthy",
        "version": "1.0.0",
        "docs": "/docs"
    }


# Health check endpoint
@app.get("/health", tags=["health"])
def health_check():
    """
    Detailed health check endpoint.
    """
    return {
        "status": "healthy",
        "active_sessions": session_store.get_session_count(),
        "service": "Court in Your Pocket API"
    }


# Watsonx connection test endpoint (for debugging)
@app.get("/api/test/watsonx", tags=["testing"])
def test_watsonx():
    """
    Test IBM watsonx connection.
    Only use this for debugging during development.
    """
    from agents.watsonx_client import test_connection
    return test_connection()


# Safety agent test endpoint (for debugging)
@app.get("/api/test/safety", tags=["testing"])
def test_safety():
    """
    Test safety agent functionality.
    Only use this for debugging during development.
    """
    from agents.safety_agent import test_safety_agent
    return test_safety_agent()


# Dynamic safety check endpoint
from pydantic import BaseModel, Field

class SafetyCheckRequest(BaseModel):
    """Request model for safety check"""
    message: str = Field(..., description="User message to check for safety")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "My landlord won't return my deposit"
            }
        }


@app.post("/api/safety/check", tags=["safety"])
def check_message_safety(request: SafetyCheckRequest):
    """
    Check if a user message is safe to process.
    
    This endpoint analyzes a single message and determines if it contains:
    - Criminal intent
    - Evidence tampering
    - Self-harm ideation
    - Threats or violence
    
    Returns safety status with emergency contacts if unsafe.
    
    **Example Request:**
    ```json
    {
        "message": "My landlord won't return my deposit"
    }
    ```
    
    **Example Response (Safe):**
    ```json
    {
        "safe": true,
        "emergency": false,
        "reason": ""
    }
    ```
    
    **Example Response (Unsafe):**
    ```json
    {
        "safe": false,
        "emergency": true,
        "reason": "Evidence tampering detected",
        "emergency_contacts": {...}
    }
    ```
    """
    from agents.safety_agent import check_safety, get_emergency_contacts
    
    # Check the message
    result = check_safety(request.message)
    
    # If unsafe, include emergency contacts
    if not result["safe"]:
        result["emergency_contacts"] = get_emergency_contacts()
    
    return result

# Made with Bob

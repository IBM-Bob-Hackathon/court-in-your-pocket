"""
Session Router
Handles session creation and management endpoints.
"""

from fastapi import APIRouter, HTTPException, status, Path
from pydantic import BaseModel, Field
from typing import Literal

# Import session_store from the same package
from . import session_store

router = APIRouter(prefix="/api/session", tags=["session"])


# Request/Response Models
class SessionStartRequest(BaseModel):
    """Request model for starting a new session"""
    language: Literal["en", "hi", "ta", "te", "kn", "mr", "bn", "gu"] = Field(
        ...,
        description="User's preferred language (English, Hindi, Tamil, Telugu, Kannada, Marathi, Bengali, or Gujarati)"
    )
    state: Literal["KA", "MH", "DL", "UP"] = Field(
        ...,
        description="User's state (Karnataka, Maharashtra, Delhi, or Uttar Pradesh)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "language": "en",
                "state": "KA"
            }
        }


class SessionStartResponse(BaseModel):
    """Response model for session creation"""
    sessionId: str = Field(..., description="Unique session identifier")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sessionId": "550e8400-e29b-41d4-a716-446655440000"
            }
        }


class SessionResponse(BaseModel):
    """Response model for session retrieval"""
    sessionId: str
    language: str
    state: str
    category: str | None
    stage: str
    safetyFlagged: bool
    confidenceScore: int | None
    createdAt: str
    lastAccessedAt: str
    extractedFacts: dict | None = None
    userDetails: dict | None = None


class UserDetailsRequest(BaseModel):
    """Request model for saving user contact details"""
    user_name: str = Field(..., description="Full name of the user")
    phone_number: str = Field(..., description="10-digit phone number")
    email_id: str = Field("", description="Email address (optional)")


# Endpoints
@router.post(
    "/start",
    response_model=SessionStartResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Start a new session",
    description="Creates a new user session with specified language and state preferences"
)
async def start_session(request: SessionStartRequest):
    """
    Create a new session for the user.
    
    This endpoint initializes a new session with:
    - Unique session ID (UUID)
    - User's language preference (en/hi)
    - User's state (KA/MH/DL)
    - Empty conversation history
    - Initial stage set to 'intake'
    
    **Mock Response for Other Developers:**
    ```json
    {
        "sessionId": "550e8400-e29b-41d4-a716-446655440000"
    }
    ```
    
    Args:
        request: SessionStartRequest containing language and state
    
    Returns:
        SessionStartResponse with the new session ID
    
    Raises:
        HTTPException: 400 if validation fails
    """
    try:
        # Create new session
        session_id = session_store.create_session(
            language=request.language,
            state=request.state
        )
        
        return SessionStartResponse(sessionId=session_id)
    
    except Exception as e:
        # Log the error internally but don't expose details to client
        print(f"Error creating session: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session"
        )


@router.get(
    "/{session_id}",
    response_model=SessionResponse,
    summary="Get session details",
    description="Retrieve session information by session ID"
)
async def get_session(
    session_id: str = Path(..., description="Session ID (UUID format)", regex="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
):
    """
    Retrieve session details.
    
    Args:
        session_id: The session ID to retrieve
    
    Returns:
        SessionResponse with session details
    
    Raises:
        HTTPException: 404 if session not found or expired
    """
    session = session_store.get_session(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired"
        )
    
    return SessionResponse(
        sessionId=session["sessionId"],
        language=session["language"],
        state=session["state"],
        category=session["category"],
        stage=session["stage"],
        safetyFlagged=session["safetyFlagged"],
        confidenceScore=session["confidenceScore"],
        createdAt=session["createdAt"],
        lastAccessedAt=session["lastAccessedAt"],
        extractedFacts=session.get("extractedFacts"),
        userDetails=session.get("userDetails"),
    )


@router.patch(
    "/{session_id}/user",
    summary="Save user contact details",
    description="Store user name, phone number, and email against the session for Dev 3"
)
async def save_user_details(
    request: UserDetailsRequest,
    session_id: str = Path(..., description="Session ID (UUID format)", pattern="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
):
    session = session_store.get_session(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found or expired"
        )
    session["userDetails"] = {
        "user_name": request.user_name,
        "phone_number": request.phone_number,
        "email_id": request.email_id,
    }
    session_store.update_session(session_id, session)
    return {"status": "ok"}


@router.delete(
    "/{session_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a session",
    description="Manually delete a session before it expires"
)
async def delete_session(
    session_id: str = Path(..., description="Session ID (UUID format)", regex="^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$")
):
    """
    Delete a session.
    
    Args:
        session_id: The session ID to delete
    
    Raises:
        HTTPException: 404 if session not found
    """
    success = session_store.delete_session(session_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return None


@router.get(
    "/health/stats",
    summary="Get session statistics",
    description="Get current session count and health status"
)
async def get_stats():
    """
    Get session statistics.
    
    Returns:
        Dictionary with active session count
    """
    return {
        "active_sessions": session_store.get_session_count(),
        "status": "healthy"
    }

# Made with Bob

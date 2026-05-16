"""
Session Store - Mock implementation
This will be replaced by Developer 1's actual implementation with proper session management
"""

from datetime import datetime, timedelta
from typing import Optional
import uuid

# In-memory session storage (will be replaced with proper implementation)
_sessions = {}

def create_session(language: str = "en", state: str = "KA") -> dict:
    """
    Create a new session
    
    Args:
        language: User's preferred language (en/hi)
        state: User's state (KA/MH/DL)
        
    Returns:
        dict: New session object
    """
    session_id = str(uuid.uuid4())
    session = {
        "sessionId": session_id,
        "language": language,
        "state": state,
        "category": None,
        "conversationHistory": [],
        "extractedFacts": {
            "issue": None,
            "partyName": None,
            "amount": None,
            "dates": [],
            "location": None
        },
        "stage": "intake",
        "safetyFlagged": False,
        "confidenceScore": None,
        "createdAt": datetime.utcnow().isoformat(),
        "expiresAt": (datetime.utcnow() + timedelta(minutes=30)).isoformat()
    }
    _sessions[session_id] = session
    return session


def get_session(session_id: str) -> Optional[dict]:
    """
    Retrieve a session by ID
    
    Args:
        session_id: Session ID to retrieve
        
    Returns:
        dict or None: Session object if found and not expired
    """
    session = _sessions.get(session_id)
    if not session:
        # Auto-create session for mock session IDs (for development)
        if session_id.startswith("mock-session-"):
            print(f"Auto-creating session for mock ID: {session_id}")
            session = create_session()
            session["sessionId"] = session_id
            _sessions[session_id] = session
            return session
        return None
    
    # Check if expired
    expires_at = datetime.fromisoformat(session["expiresAt"])
    if datetime.utcnow() > expires_at:
        del _sessions[session_id]
        return None
    
    return session


def update_session(session_id: str, session: dict) -> bool:
    """
    Update an existing session
    
    Args:
        session_id: Session ID to update
        session: Updated session object
        
    Returns:
        bool: True if updated successfully
    """
    if session_id not in _sessions:
        return False
    
    # Extend expiry time
    session["expiresAt"] = (datetime.utcnow() + timedelta(minutes=30)).isoformat()
    _sessions[session_id] = session
    return True


def delete_session(session_id: str) -> bool:
    """
    Delete a session
    
    Args:
        session_id: Session ID to delete
        
    Returns:
        bool: True if deleted successfully
    """
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False

# Made with Bob

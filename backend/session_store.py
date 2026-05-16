"""
Session Store for Court in Your Pocket
In-memory session management with 30-minute expiry
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional

# In-memory session storage
_sessions: Dict[str, Dict] = {}

# Session expiry time (30 minutes)
SESSION_EXPIRY_MINUTES = 30


def create_session(language: str = "en", state: str = "KA") -> str:
    """
    Create a new session
    
    Args:
        language: User's preferred language (en/hi)
        state: User's state (KA/MH/DL)
    
    Returns:
        Session ID (UUID)
    """
    session_id = str(uuid.uuid4())
    
    _sessions[session_id] = {
        "sessionId": session_id,
        "language": language,
        "state": state,
        "category": None,
        "conversationHistory": [],
        "extractedFacts": {
            "issue": None,
            "partyName": None,
            "amounts": None,
            "dates": [],
            "location": None
        },
        "stage": "intake",
        "safetyFlagged": False,
        "confidenceScore": None,
        "createdAt": datetime.utcnow(),
        "lastAccessedAt": datetime.utcnow()
    }
    
    return session_id


def get_session(session_id: str) -> Optional[Dict]:
    """
    Get session by ID
    
    Args:
        session_id: Session ID
    
    Returns:
        Session dictionary or None if not found/expired
    """
    if session_id not in _sessions:
        return None
    
    session = _sessions[session_id]
    
    # Check if session has expired
    last_accessed = session.get("lastAccessedAt")
    if last_accessed:
        expiry_time = last_accessed + timedelta(minutes=SESSION_EXPIRY_MINUTES)
        if datetime.utcnow() > expiry_time:
            # Session expired, remove it
            del _sessions[session_id]
            return None
    
    # Update last accessed time
    session["lastAccessedAt"] = datetime.utcnow()
    
    return session


def update_session(session_id: str, updates: Dict) -> bool:
    """
    Update session with new data
    
    Args:
        session_id: Session ID
        updates: Dictionary of fields to update
    
    Returns:
        True if successful, False if session not found
    """
    session = get_session(session_id)
    if not session:
        return False
    
    # Update fields
    for key, value in updates.items():
        if key in session:
            # For nested dicts like extractedFacts, merge instead of replace
            if isinstance(session[key], dict) and isinstance(value, dict):
                session[key].update(value)
            else:
                session[key] = value
    
    session["lastAccessedAt"] = datetime.utcnow()
    
    return True


def delete_session(session_id: str) -> bool:
    """
    Delete a session
    
    Args:
        session_id: Session ID
    
    Returns:
        True if deleted, False if not found
    """
    if session_id in _sessions:
        del _sessions[session_id]
        return True
    return False


def cleanup_expired_sessions():
    """Remove all expired sessions"""
    current_time = datetime.utcnow()
    expired_sessions = []
    
    for session_id, session in _sessions.items():
        last_accessed = session.get("lastAccessedAt")
        if last_accessed:
            expiry_time = last_accessed + timedelta(minutes=SESSION_EXPIRY_MINUTES)
            if current_time > expiry_time:
                expired_sessions.append(session_id)
    
    for session_id in expired_sessions:
        del _sessions[session_id]
    
    return len(expired_sessions)


# Made with Bob
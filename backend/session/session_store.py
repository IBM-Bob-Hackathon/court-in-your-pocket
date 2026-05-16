"""
Session Store Module
Manages in-memory session storage with automatic expiry.
Thread-safe implementation for concurrent access.
"""

import uuid
from datetime import datetime, timedelta
from threading import Lock
from typing import Dict, Optional
import os
from dotenv import load_dotenv

load_dotenv()

# Global session storage
_sessions: Dict[str, dict] = {}
_lock = Lock()

# Configuration
SESSION_EXPIRY_MINUTES = int(os.getenv("SESSION_EXPIRY_MINUTES", "30"))


def create_session(language: str, state: str) -> str:
    """
    Create a new session with a unique ID.
    
    Args:
        language: User's preferred language ('en' or 'hi')
        state: User's state ('KA', 'MH', or 'DL')
    
    Returns:
        str: Unique session ID (UUID)
    """
    session_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    session_data = {
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
        "createdAt": now.isoformat(),
        "lastAccessedAt": now.isoformat()
    }
    
    with _lock:
        _sessions[session_id] = session_data
    
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    """
    Retrieve a session by ID.
    
    Note: This function performs expiry checking and deletion within a single
    lock acquisition, ensuring thread-safe access. The time-based expiry check
    is atomic with respect to other operations on the session store.
    
    Args:
        session_id: The session ID to retrieve
    
    Returns:
        dict: Session data if found and not expired, None otherwise
    """
    with _lock:
        session = _sessions.get(session_id)
        
        if not session:
            return None
        
        # Check if session has expired
        last_accessed = datetime.fromisoformat(session["lastAccessedAt"])
        expiry_time = last_accessed + timedelta(minutes=SESSION_EXPIRY_MINUTES)
        
        if datetime.utcnow() > expiry_time:
            # Session expired, remove it
            del _sessions[session_id]
            return None
        
        # Update last accessed time
        session["lastAccessedAt"] = datetime.utcnow().isoformat()
        return session


def update_session(session_id: str, updates: dict) -> bool:
    """
    Update an existing session with new data.
    
    Args:
        session_id: The session ID to update
        updates: Dictionary of fields to update
    
    Returns:
        bool: True if update successful, False if session not found
    """
    with _lock:
        session = _sessions.get(session_id)
        
        if not session:
            return False
        
        # Update fields
        for key, value in updates.items():
            if key in session:
                session[key] = value
        
        # Update last accessed time
        session["lastAccessedAt"] = datetime.utcnow().isoformat()
        return True


def delete_session(session_id: str) -> bool:
    """
    Delete a session.
    
    Args:
        session_id: The session ID to delete
    
    Returns:
        bool: True if deleted, False if not found
    """
    with _lock:
        if session_id in _sessions:
            del _sessions[session_id]
            return True
        return False


def cleanup_expired_sessions() -> int:
    """
    Remove all expired sessions from storage.
    
    Returns:
        int: Number of sessions cleaned up
    """
    now = datetime.utcnow()
    expired_ids = []
    
    with _lock:
        # Create a list copy to avoid dictionary size change during iteration
        for session_id, session in list(_sessions.items()):
            last_accessed = datetime.fromisoformat(session["lastAccessedAt"])
            expiry_time = last_accessed + timedelta(minutes=SESSION_EXPIRY_MINUTES)
            
            if now > expiry_time:
                expired_ids.append(session_id)
        
        # Remove expired sessions
        for session_id in expired_ids:
            del _sessions[session_id]
    
    return len(expired_ids)


def get_session_count() -> int:
    """
    Get the total number of active sessions.
    
    Returns:
        int: Number of active sessions
    """
    with _lock:
        return len(_sessions)

# Made with Bob

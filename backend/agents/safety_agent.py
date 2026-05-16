"""
Safety Agent - Mock implementation
This will be replaced by Developer 1's actual implementation
"""

async def check_safety(message: str) -> dict:
    """
    Mock safety check - always returns safe
    
    Real implementation by Developer 1 will use IBM watsonx to detect:
    - Criminal activity
    - Evidence tampering
    - Self-harm
    
    Args:
        message: User's message to check
        
    Returns:
        dict: {"safe": bool, "emergency": bool}
    """
    # Mock implementation - check for obvious dangerous keywords
    dangerous_keywords = [
        "kill", "murder", "weapon", "bomb", "suicide", "harm myself",
        "destroy evidence", "hide evidence", "fake documents"
    ]
    
    message_lower = message.lower()
    is_dangerous = any(keyword in message_lower for keyword in dangerous_keywords)
    
    return {
        "safe": not is_dangerous,
        "emergency": is_dangerous
    }

# Made with Bob

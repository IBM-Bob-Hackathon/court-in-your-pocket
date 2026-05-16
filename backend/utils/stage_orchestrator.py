"""
Stage Orchestrator - Manages conversation stage transitions
"""

def should_transition_to_analysis(extracted_facts: dict) -> bool:
    """
    Determine if we have enough facts to move to analysis stage
    
    Required: issue, location
    Optional: At least 2 of: partyName, amount, dates
    
    Args:
        extracted_facts: Dictionary containing extracted facts
        
    Returns:
        bool: True if ready to transition to analysis
    """
    required = ["issue", "location"]
    
    # Check required fields
    for field in required:
        if not extracted_facts.get(field):
            return False
    
    # Check optional fields - must have actual values
    filled_optional = 0
    if extracted_facts.get("partyName"):
        filled_optional += 1
    if extracted_facts.get("amount"):
        filled_optional += 1
    if extracted_facts.get("dates") and len(extracted_facts.get("dates", [])) > 0:
        filled_optional += 1
    
    return filled_optional >= 2


def count_intake_questions(conversation_history: list) -> int:
    """
    Count how many questions Bob has asked during intake
    
    Used to enforce max 5-6 questions rule
    
    Args:
        conversation_history: List of conversation messages
        
    Returns:
        int: Number of questions asked by Bob
    """
    bob_messages = [
        msg for msg in conversation_history 
        if msg.get("role") == "assistant"
    ]
    
    # Count messages ending with "?"
    questions = [msg for msg in bob_messages if msg.get("content", "").endswith("?")]
    
    return len(questions)


def get_progress_step(stage: str) -> tuple:
    """
    Map stage to progress tracker display
    
    Args:
        stage: Current conversation stage
        
    Returns:
        tuple: (step_number, label)
    """
    stage_map = {
        "intake": (1, "Understanding your situation"),
        "analysis": (2, "Analyzing your rights"),
        "document": (3, "Preparing your documents"),
        "complete": (4, "Your action plan is ready")
    }
    return stage_map.get(stage, (1, "Getting started"))


def format_history_for_bob(conversation_history: list, extracted_facts: dict) -> str:
    """
    Format conversation history into a prompt-friendly string
    
    Includes:
    - All user/assistant messages
    - Current extracted facts as context
    
    Args:
        conversation_history: List of conversation messages
        extracted_facts: Dictionary of extracted facts
        
    Returns:
        str: Formatted history string
    """
    formatted = "=== Conversation History ===\n\n"
    
    # Last 20 messages only to avoid token limits
    for msg in conversation_history[-20:]:
        role = "User" if msg.get("role") == "user" else "Bob"
        content = msg.get("content", "")
        formatted += f"{role}: {content}\n\n"
    
    formatted += "\n=== Extracted Facts So Far ===\n"
    for key, value in extracted_facts.items():
        if value:
            if isinstance(value, list):
                formatted += f"- {key}: {', '.join(str(v) for v in value)}\n"
            else:
                formatted += f"- {key}: {value}\n"
    
    return formatted


def trim_conversation_history(history: list, max_messages: int = 20) -> list:
    """
    Keep only the most recent messages to avoid token limits
    
    Always keep first message (Bob's greeting)
    
    Args:
        history: List of conversation messages
        max_messages: Maximum number of messages to keep
        
    Returns:
        list: Trimmed conversation history
    """
    if len(history) <= max_messages:
        return history
    
    # Keep first message + last (max_messages - 1)
    return [history[0]] + history[-(max_messages - 1):]

# Made with Bob

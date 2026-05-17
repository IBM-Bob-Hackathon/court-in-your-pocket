"""
Stage Orchestrator - Manages conversation stage transitions
"""

# Category-specific required fields (must match intake_agent.py CATEGORIES)
CATEGORY_REQUIRED_FIELDS = {
    "tenant":           ["issue", "location", "partyName", "amount", "dates"],
    "employment":       ["issue", "location", "partyName", "amount", "dates"],
    "consumer":         ["issue", "location", "partyName", "amount", "dates"],
    "theft":            ["issue", "location", "amount", "dates"],
    "harassment":       ["issue", "location", "dates"],
    "property":         ["issue", "location", "partyName", "dates"],
    "police_complaint": ["issue", "location", "dates"],
    "general":          ["issue", "location", "dates"],
}


def should_transition_to_analysis(extracted_facts: dict, category: str = None) -> bool:
    """
    Check if all mandatory fields for the detected category are filled.
    Falls back to requiring issue + location + dates if category unknown.
    Note: extraInfoAsked must also be True (open question was asked and answered).
    """
    # The intake agent sets extraInfoAsked=True before marking readyForAnalysis
    # Transition is only allowed after the open "anything else?" was handled
    if not extracted_facts.get("extraInfoAsked"):
        return False

    required = CATEGORY_REQUIRED_FIELDS.get(category or "general", ["issue", "location", "dates"])

    for field in required:
        val = extracted_facts.get(field)
        if field == "dates":
            if not val or len(val) == 0:
                return False
        else:
            if not val:
                return False

    return True


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

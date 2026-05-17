from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.safety_agent import check_safety
from agents.intake_agent import process_intake
from session.session_store import get_session, update_session
from utils.stage_orchestrator import (
    should_transition_to_analysis,
    count_intake_questions,
    format_history_for_bob,
    trim_conversation_history
)

router = APIRouter(prefix="/api/chat", tags=["chat"])

class MessageRequest(BaseModel):
    sessionId: str
    message: str

class MessageResponse(BaseModel):
    reply: str
    stage: str
    chips: List[str]
    safetyBlocked: bool
    extractedFacts: Optional[dict] = None

class InitSessionRequest(BaseModel):
    language: str = "en"
    state: str = "KA"

class InitSessionResponse(BaseModel):
    sessionId: str
    language: str
    state: str

@router.post("/init", response_model=InitSessionResponse)
async def init_session(request: InitSessionRequest):
    """
    Initialize a new session
    """
    from session.session_store import create_session
    session_id = create_session(language=request.language, state=request.state)
    return InitSessionResponse(
        sessionId=session_id,
        language=request.language,
        state=request.state
    )

@router.post("/message")
async def send_message(request: MessageRequest):
    """
    Main chat endpoint - orchestrates conversation flow
    
    Pipeline:
    1. Get session from store
    2. Safety check (call Dev 1's agent)
    3. Add message to conversation history
    4. Route based on stage:
       - intake: call Intake Agent
       - analysis: call Dev 3's endpoint
       - document/complete: return guidance
    5. Update session
    6. Return response
    """
    
    # Step 1: Get session
    session = get_session(request.sessionId)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found or expired")
    
    # Handle initial greeting request
    if request.message == "__INIT__":
        greeting = "Namaste! What legal issue are you facing today?" if session["language"] == "en" else "नमस्ते! आप किस कानूनी समस्या का सामना कर रहे हैं?"
        return MessageResponse(
            reply=greeting,
            stage=session["stage"],
            chips=[],
            safetyBlocked=False,
            extractedFacts=session["extractedFacts"]
        )
    
    # Step 2: Safety check
    safety_result = check_safety(request.message)
    if not safety_result["safe"]:
        session["safetyFlagged"] = True
        update_session(request.sessionId, session)
        return MessageResponse(
            reply="I cannot assist with this type of issue. Please contact emergency services.",
            stage=session["stage"],
            chips=[],
            safetyBlocked=True,
            extractedFacts=session["extractedFacts"]
        )
    
    # Step 3: Add to conversation history
    session["conversationHistory"].append({
        "role": "user",
        "content": request.message,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    # Trim history to avoid token limits
    session["conversationHistory"] = trim_conversation_history(session["conversationHistory"])
    
    # Step 4: Route based on stage
    if session["stage"] == "intake":
        # Check question limit — raised to 10 to allow all 5 facts to be collected
        question_count = count_intake_questions(session["conversationHistory"])
        if question_count >= 10:
            # Force transition even if not all facts collected
            session["stage"] = "analysis"
            reply = "Thank you for the information. Let me analyze your situation now."
            session["conversationHistory"].append({
                "role": "assistant",
                "content": reply,
                "timestamp": datetime.utcnow().isoformat()
            })
            update_session(request.sessionId, session)
            return MessageResponse(
                reply=reply,
                stage="analysis",
                chips=[],
                safetyBlocked=False,
                extractedFacts=session["extractedFacts"]
            )
        
        # Format history for Bob
        formatted_history = format_history_for_bob(
            session["conversationHistory"],
            session["extractedFacts"]
        )
        
        # Call intake agent
        response = await process_intake(session, request.message, formatted_history)

        # Update extracted facts and category
        session["extractedFacts"] = response["extractedFacts"]
        if response.get("category"):
            session["category"] = response["category"]

        # Transition: trust the intake agent's readyForAnalysis flag
        if response.get("readyForAnalysis", False):
            session["stage"] = "analysis"
        
        # Add Bob's reply to history
        session["conversationHistory"].append({
            "role": "assistant",
            "content": response["reply"],
            "timestamp": datetime.utcnow().isoformat()
        })
        
        update_session(request.sessionId, session)
        
        return MessageResponse(
            reply=response["reply"],
            stage=session["stage"],
            chips=response.get("chips", []),
            safetyBlocked=False,
            extractedFacts=session["extractedFacts"]
        )
    
    elif session["stage"] == "analysis":
        # This stage is handled by Dev 3
        # Just acknowledge and wait
        reply = "I'm analyzing your legal situation. This will take a moment..."
        session["conversationHistory"].append({
            "role": "assistant",
            "content": reply,
            "timestamp": datetime.utcnow().isoformat()
        })
        update_session(request.sessionId, session)
        
        return MessageResponse(
            reply=reply,
            stage="analysis",
            chips=[],
            safetyBlocked=False,
            extractedFacts=session["extractedFacts"]
        )
    
    else:
        # document or complete stage
        reply = "Your action plan is ready. Please proceed to the next screen."
        session["conversationHistory"].append({
            "role": "assistant",
            "content": reply,
            "timestamp": datetime.utcnow().isoformat()
        })
        update_session(request.sessionId, session)
        
        return MessageResponse(
            reply=reply,
            stage=session["stage"],
            chips=[],
            safetyBlocked=False,
            extractedFacts=session["extractedFacts"]
        )

# Made with Bob

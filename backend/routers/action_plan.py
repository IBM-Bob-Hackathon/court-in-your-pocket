from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field
from typing import List, Optional

from agents.action_plan_agent import (
    action_plan_agent,
    document_generator,
    get_session_data,
    ActionStep
)


# ============================================================================
# Pydantic Request/Response Models
# ============================================================================

class ActionPlanRequest(BaseModel):
    """Request model for action plan generation endpoint."""
    sessionId: str = Field(..., description="Unique session identifier")
    category: str = Field(..., description="Legal category (e.g., 'Tenant Rights')")
    sub_scenario: str = Field(..., description="Specific legal scenario")
    option: str = Field(..., description="User's chosen action: 'A' (Demand Letter), 'B' (File Complaint), or 'C' (Free Legal Aid)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sessionId": "session_123",
                "category": "employment",
                "sub_scenario": "delayed_or_unpaid_wages",
                "option": "A"
            }
        }


class ActionPlanResponse(BaseModel):
    """Response model for action plan generation endpoint."""
    steps: List[ActionStep] = Field(..., description="List of actionable steps with time estimates")
    
    class Config:
        json_schema_extra = {
            "example": {
                "steps": [
                    {
                        "step_number": 1,
                        "instruction": "Draft a formal demand letter to your landlord requesting the return of your security deposit",
                        "time_estimate": "2-3 hours"
                    },
                    {
                        "step_number": 2,
                        "instruction": "Send the demand letter via registered post with acknowledgment due",
                        "time_estimate": "1 day"
                    }
                ]
            }
        }


class DocumentRequest(BaseModel):
    """Request model for document generation endpoint."""
    sessionId: str = Field(..., description="Unique session identifier")
    category: Optional[str] = Field(None, description="Legal category (e.g., 'Tenant Rights', 'Consumer Protection', 'Employment')")
    option: Optional[str] = Field(None, description="User's chosen action: 'A' (Demand Letter), 'B' (File Complaint), or 'C' (Free Legal Aid)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "sessionId": "session_123",
                "category": "Tenant Rights",
                "option": "A"
            }
        }


class DocumentResponse(BaseModel):
    """Response model for document generation endpoint."""
    documentText: str = Field(..., description="Generated document with all placeholders replaced")
    
    class Config:
        json_schema_extra = {
            "example": {
                "documentText": "Dear John Doe,\n\nThis is a formal notice regarding Security Deposit Not Returned...\n\nSincerely,\nRajesh Kumar"
            }
        }


# ============================================================================
# FastAPI Router
# ============================================================================

router = APIRouter(
    prefix="/api",
    tags=["Action Plan & Documents"],
    responses={
        404: {"description": "Session not found"},
        500: {"description": "Internal server error"}
    }
)


@router.post(
    "/action-plan/generate",
    response_model=ActionPlanResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Action Plan",
    description="""
    Generate a step-by-step action plan for a user's legal issue using AI.
    
    This endpoint uses OpenAI's LLM with structured outputs to create a tailored,
    actionable plan based on the user's category, scenario, and chosen option.
    
    **Options:**
    - **A**: Demand Letter
    - **B**: File Complaint
    - **C**: Free Legal Aid
    
    The plan will contain 4-5 specific steps with realistic time estimates,
    all tailored to Indian law and procedures.
    """
)
async def generate_action_plan(request: ActionPlanRequest) -> ActionPlanResponse:
    """
    Generate an AI-powered action plan for the user's legal issue.
    
    Process:
    1. Validates the session exists
    2. Retrieves user's extracted facts from session
    3. Calls the ActionPlanAgent with LLM to generate steps
    4. Returns structured action plan with 4-5 steps
    
    Args:
        request: ActionPlanRequest containing sessionId, category, sub_scenario, and option
        
    Returns:
        ActionPlanResponse with list of actionable steps
        
    Raises:
        HTTPException 404: If session not found
        HTTPException 400: If option is invalid
        HTTPException 500: If LLM generation fails
    """
    
    # Validate option
    valid_options = ["A", "B", "C"]
    if request.option not in valid_options:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid option '{request.option}'. Must be one of: {', '.join(valid_options)}"
        )
    
    # Validate session exists (optional check, agent will also check)
    session_data = get_session_data(request.sessionId)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {request.sessionId}"
        )
    
    try:
        # Generate action plan using LLM agent
        # Agent will fetch session data and extracted facts internally
        action_plan = action_plan_agent.generate_action_plan(
            session_id=request.sessionId,
            category=request.category,
            sub_scenario=request.sub_scenario,
            option=request.option
        )
        
        return ActionPlanResponse(steps=action_plan.steps)
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate action plan: {str(e)}"
        )


@router.post(
    "/document/generate",
    response_model=DocumentResponse,
    status_code=status.HTTP_200_OK,
    summary="Generate Legal Document",
    description="""
    Generate a legal document by replacing template placeholders with user data.
    
    This endpoint:
    1. Fetches the user's session data and extracted facts
    2. Loads the appropriate document template based on category and option
    3. Performs string replacement of {{placeholders}} with actual values
    4. Returns the complete document text
    
    Templates contain placeholders like {{landlord_name}}, {{deposit_amount}}, etc.
    which are replaced with values from the session's extractedFacts dictionary.
    """
)
async def generate_document(request: DocumentRequest) -> DocumentResponse:
    """
    Generate a legal document by replacing template placeholders with user data.
    
    Process:
    1. Validates the session exists
    2. Retrieves user's extracted facts and context (category, option)
    3. Loads appropriate template file
    4. Replaces all {{placeholder}} tokens with actual values
    5. Returns complete document text
    
    Args:
        request: DocumentRequest containing sessionId
        
    Returns:
        DocumentResponse with complete document text
        
    Raises:
        HTTPException 404: If session not found
        HTTPException 500: If document generation fails
    """
    
    # Fetch session data
    session_data = get_session_data(request.sessionId)
    if not session_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Session not found: {request.sessionId}"
        )
    
    try:
        # Generate document using template replacement
        document_text = document_generator.generate_document(
            session_id=request.sessionId,
            category=request.category,
            option=request.option
        )
        
        return DocumentResponse(documentText=document_text)
        
    except ValueError as e:
        # Session not found (already handled above, but kept for safety)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate document: {str(e)}"
        )


# ============================================================================
# Health Check Endpoint (Optional but Recommended)
# ============================================================================

@router.get(
    "/action-plan/health",
    status_code=status.HTTP_200_OK,
    summary="Health Check",
    description="Check if the action plan service is running"
)
async def health_check():
    """
    Simple health check endpoint to verify the service is operational.
    
    Returns:
        Dictionary with status and service information
    """
    return {
        "status": "healthy",
        "service": "Action Plan & Document Generator",
        "endpoints": [
            "/api/action-plan/generate",
            "/api/document/generate"
        ]
    }

# Made with Bob

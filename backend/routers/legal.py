"""
Legal Router for Court in Your Pocket
Handles legal analysis and resource retrieval
"""

import os
import json
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from session.session_store import get_session, update_session
from agents.classifier_agent import classify_issue
from agents.analysis_agent import analyze_rights

router = APIRouter(prefix="/api/legal", tags=["legal"])

# Constants
FALLBACK_LAW_ENTRIES_COUNT = 2


# Pydantic Models
class AnalyzeRequest(BaseModel):
    sessionId: str
    language: str = "en"


class RightEntry(BaseModel):
    law_name: str
    section: str
    plain_english: str
    exact_quote: str
    confidence: int
    last_verified: str
    source_url: str


class ActionOption(BaseModel):
    id: str
    label: str


class AnalyzeResponse(BaseModel):
    rights: List[RightEntry]
    confidence: int
    deadline: int
    options: List[ActionOption]


class OutOfScopeResponse(BaseModel):
    outOfScope: bool
    message: str
    legalAid: List[Dict[str, str]]


class ResourcesResponse(BaseModel):
    state: str
    helplines: List[Dict[str, str]]
    portals: List[Dict[str, str]]
    legalAid: List[Dict[str, str]]


# Helper Functions
def _load_legal_data(category: str) -> List[Dict]:
    """
    Load legal data from JSON files
    
    Args:
        category: One of "tenant", "employment", "consumer"
    
    Returns:
        List of law entries
    """
    category_file_map = {
        "tenant": "tenant_laws.json",
        "employment": "employment_laws.json",
        "consumer": "consumer_laws.json"
    }
    
    if category not in category_file_map:
        return []
    
    file_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        "data",
        category_file_map[category]
    )
    
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data if isinstance(data, list) else []
    except FileNotFoundError:
        print(f"Warning: Legal data file not found: {file_path}")
        return []
    except json.JSONDecodeError as e:
        print(f"Error parsing legal data file {file_path}: {e}")
        return []


def _filter_laws_by_jurisdiction_and_keywords(
    law_entries: List[Dict],
    state: str,
    issue_text: str
) -> List[Dict]:
    """
    Filter law entries by jurisdiction and keyword matching
    
    Args:
        law_entries: List of law entries from JSON
        state: User's state (e.g., "KA", "MH", "DL")
        issue_text: User's issue description
    
    Returns:
        Filtered list of matching law entries
    """
    if not law_entries:
        return []
    
    issue_lower = issue_text.lower() if issue_text else ""
    matched_entries = []
    
    for entry in law_entries:
        # Check jurisdiction match
        jurisdiction = entry.get("jurisdiction", [])
        if state not in jurisdiction and "IN" not in jurisdiction:
            continue
        
        # Check keyword match
        keywords = entry.get("keywords", [])
        if keywords:
            # Check if any keyword appears in the issue text
            keyword_match = any(
                keyword.lower() in issue_lower
                for keyword in keywords
            )
            if keyword_match:
                matched_entries.append(entry)
    
    return matched_entries


def _get_out_of_scope_response() -> Dict:
    """
    Generate out-of-scope response with legal aid contacts
    
    Returns:
        Dictionary with outOfScope flag, message, and legal aid contacts
    """
    return {
        "outOfScope": True,
        "message": "This issue falls outside our current scope (tenant, employment, consumer rights). We recommend contacting free legal aid services.",
        "legalAid": [
            {
                "name": "National Legal Services Authority (NALSA)",
                "phone": "011-23388952",
                "website": "https://nalsa.gov.in",
                "description": "Free legal aid for eligible citizens"
            },
            {
                "name": "State Legal Services Authority",
                "phone": "Varies by state",
                "website": "https://nalsa.gov.in/state-legal-services-authorities",
                "description": "State-level free legal aid"
            },
            {
                "name": "District Legal Services Authority",
                "phone": "Contact local district court",
                "website": "Visit nearest district court",
                "description": "District-level legal aid and advice"
            }
        ]
    }


def _get_default_action_options() -> List[Dict]:
    """
    Get default action options for legal analysis
    
    Returns:
        List of action options
    """
    return [
        {"id": "A", "label": "Send demand letter"},
        {"id": "B", "label": "File complaint"},
        {"id": "C", "label": "Free legal aid"}
    ]


# API Endpoints
@router.post("/analyze")
async def analyze_legal_issue(request: AnalyzeRequest):
    """
    Analyze user's legal issue and provide rights information
    
    Process:
    1. Get session and extract facts
    2. Classify the issue
    3. If out of scope, return legal aid contacts
    4. Otherwise, retrieve relevant laws
    5. Analyze rights using AI
    6. Return rights with action options
    """
    try:
        # Get session
        session = get_session(request.sessionId)
        if not session:
            raise HTTPException(status_code=404, detail="Session not found or expired")
        
        # Extract facts and state
        extracted_facts = session.get("extractedFacts", {})
        state = session.get("state", "KA")

        # Inject user_name into facts so the analysis agent addresses the right person
        user_details = session.get("userDetails") or {}
        user_name = user_details.get("user_name")
        if user_name:
            extracted_facts = {**extracted_facts, "user_name": user_name}
        
        # Validate that we have enough facts
        if not extracted_facts.get("issue"):
            raise HTTPException(
                status_code=400,
                detail="Insufficient facts extracted. Please complete the intake conversation first."
            )
        
        # Step 1: Classify the issue
        classification = await classify_issue(extracted_facts)
        category = classification.get("category")
        sub_scenario = classification.get("sub_scenario")
        
        # Update session with classification
        update_session(request.sessionId, {
            "category": category,
            "sub_scenario": sub_scenario
        })
        
        # Step 2: Check if out of scope
        if category == "out_of_scope":
            return _get_out_of_scope_response()
        
        # Step 3: Load relevant legal data
        if not category:
            category = "out_of_scope"
        law_entries = _load_legal_data(category)
        
        if not law_entries:
            raise HTTPException(
                status_code=500,
                detail=f"Legal data not available for category: {category}"
            )
        
        # Step 4: Filter laws by jurisdiction and keywords
        issue_text = extracted_facts.get("issue", "")
        matched_entries = _filter_laws_by_jurisdiction_and_keywords(
            law_entries,
            state,
            issue_text
        )
        
        # If no keyword match, use first entries as fallback
        if not matched_entries:
            print(f"No keyword match found, using fallback (first {FALLBACK_LAW_ENTRIES_COUNT} entries)")
            matched_entries = law_entries[:FALLBACK_LAW_ENTRIES_COUNT]
        
        # Step 5: Analyze rights using AI
        analysis_result = await analyze_rights(extracted_facts, matched_entries, request.language)
        
        # Step 6: Format and return response
        rights = analysis_result.get("rights", [])
        confidence = analysis_result.get("confidence", 3)
        deadline = analysis_result.get("deadline", 30)
        
        # Update session with analysis results
        update_session(request.sessionId, {
            "confidenceScore": confidence,
            "stage": "analysis"
        })
        
        return {
            "rights": rights,
            "confidence": confidence,
            "deadline": deadline,
            "options": _get_default_action_options()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in analyze_legal_issue: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/resources")
async def get_legal_resources(state: str = "KA"):
    """
    Get legal resources, helplines, and portals for a specific state
    
    Args:
        state: State code (KA, MH, DL)
    
    Returns:
        Dictionary with helplines, portals, and legal aid contacts
    """
    try:
        # State-specific resources
        state_resources = {
            "KA": {
                "helplines": [
                    {
                        "name": "Karnataka State Legal Services Authority",
                        "phone": "080-22867926",
                        "description": "Free legal aid and advice"
                    },
                    {
                        "name": "Karnataka Consumer Helpline",
                        "phone": "1800-425-9339",
                        "description": "Consumer complaints and guidance"
                    }
                ],
                "portals": [
                    {
                        "name": "Karnataka Rent Authority",
                        "url": "https://karnataka.gov.in",
                        "description": "Tenant-landlord dispute resolution"
                    },
                    {
                        "name": "Karnataka Labour Department",
                        "url": "https://labour.karnataka.gov.in",
                        "description": "Employment and wage disputes"
                    }
                ],
                "legalAid": [
                    {
                        "name": "Karnataka State Legal Services Authority",
                        "phone": "080-22867926",
                        "website": "https://kslsa.kar.nic.in",
                        "description": "Free legal aid for eligible citizens"
                    }
                ]
            },
            "MH": {
                "helplines": [
                    {
                        "name": "Maharashtra State Legal Services Authority",
                        "phone": "022-22620208",
                        "description": "Free legal aid and advice"
                    },
                    {
                        "name": "Maharashtra Consumer Helpline",
                        "phone": "1800-22-4477",
                        "description": "Consumer complaints and guidance"
                    }
                ],
                "portals": [
                    {
                        "name": "Maharashtra Rent Authority",
                        "url": "https://maharashtra.gov.in",
                        "description": "Tenant-landlord dispute resolution"
                    },
                    {
                        "name": "Maharashtra Labour Department",
                        "url": "https://mahakamgar.maharashtra.gov.in",
                        "description": "Employment and wage disputes"
                    }
                ],
                "legalAid": [
                    {
                        "name": "Maharashtra State Legal Services Authority",
                        "phone": "022-22620208",
                        "website": "https://mslsa.gov.in",
                        "description": "Free legal aid for eligible citizens"
                    }
                ]
            },
            "DL": {
                "helplines": [
                    {
                        "name": "Delhi State Legal Services Authority",
                        "phone": "011-23389150",
                        "description": "Free legal aid and advice"
                    },
                    {
                        "name": "Delhi Consumer Helpline",
                        "phone": "1800-11-4000",
                        "description": "Consumer complaints and guidance"
                    }
                ],
                "portals": [
                    {
                        "name": "Delhi Rent Authority",
                        "url": "https://delhi.gov.in",
                        "description": "Tenant-landlord dispute resolution"
                    },
                    {
                        "name": "Delhi Labour Department",
                        "url": "https://labour.delhi.gov.in",
                        "description": "Employment and wage disputes"
                    }
                ],
                "legalAid": [
                    {
                        "name": "Delhi State Legal Services Authority",
                        "phone": "011-23389150",
                        "website": "https://dslsa.org",
                        "description": "Free legal aid for eligible citizens"
                    }
                ]
            },
            "UP": {
                "helplines": [
                    {
                        "name": "UP State Legal Services Authority",
                        "phone": "0522-2209340",
                        "description": "Free legal aid and advice"
                    },
                    {
                        "name": "UP Consumer Helpline",
                        "phone": "1800-180-5512",
                        "description": "Consumer complaints and guidance"
                    }
                ],
                "portals": [
                    {
                        "name": "UP Rent Authority",
                        "url": "https://up.gov.in",
                        "description": "Tenant-landlord dispute resolution"
                    },
                    {
                        "name": "UP Labour Department",
                        "url": "https://uplabour.gov.in",
                        "description": "Employment and wage disputes"
                    }
                ],
                "legalAid": [
                    {
                        "name": "UP State Legal Services Authority",
                        "phone": "0522-2209340",
                        "website": "https://upslsa.up.nic.in",
                        "description": "Free legal aid for eligible citizens"
                    }
                ]
            }
        }
        
        # Get state-specific resources or default to KA
        resources = state_resources.get(state, state_resources["KA"])
        
        # Always include national resources
        national_helplines = [
            {
                "name": "National Consumer Helpline",
                "phone": "1800-11-4000",
                "description": "National consumer complaints helpline"
            },
            {
                "name": "National Legal Services Authority (NALSA)",
                "phone": "011-23388952",
                "description": "National free legal aid authority"
            }
        ]
        
        national_portals = [
            {
                "name": "edaakhil Portal",
                "url": "https://edaakhil.nic.in",
                "description": "National consumer complaints portal"
            },
            {
                "name": "India Code",
                "url": "https://indiacode.nic.in",
                "description": "Official repository of Indian laws"
            }
        ]
        
        # Combine state and national resources
        all_helplines = national_helplines + resources["helplines"]
        all_portals = national_portals + resources["portals"]
        
        return {
            "state": state,
            "helplines": all_helplines,
            "portals": all_portals,
            "legalAid": resources["legalAid"]
        }
        
    except Exception as e:
        print(f"Error in get_legal_resources: {e}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# Made with Bob
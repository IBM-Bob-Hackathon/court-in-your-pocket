"""
Intake Agent - IBM watsonx powered fact extraction and conversation
"""

import os
import json
import re
from typing import Dict, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# IBM watsonx configuration
WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

# Check if watsonx is configured
WATSONX_ENABLED = bool(WATSONX_API_KEY and WATSONX_PROJECT_ID)

if WATSONX_ENABLED:
    try:
        from ibm_watsonx_ai.foundation_models import Model
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    except ImportError:
        WATSONX_ENABLED = False
        print("Warning: ibm-watsonx-ai not installed. Using fallback mode.")

INTAKE_SYSTEM_PROMPT = """You are a legal intake assistant for "Court in Your Pocket", an AI legal companion for Indians who cannot afford lawyers.

Your role:
1. Extract facts from the user's description of their legal issue
2. Ask ONE clarifying question at a time
3. Be empathetic but professional
4. Do NOT give legal advice yet - just gather information
5. Respond in the same language as the user (English or Hindi)

Facts to extract:
- issue: What is the legal problem? (e.g., "security deposit not returned", "salary not paid", "defective product")
- location: Which city/state? (needed to apply correct laws)
- partyName: Who is the other party? (landlord, employer, company name)
- amount: Any money involved? (in ₹)
- dates: When did this happen? (move-out date, termination date, purchase date, etc.)

Rules:
- Ask about the most important missing fact first
- Keep questions simple and conversational
- If user is emotional, acknowledge their feelings first
- After 4-5 facts are collected, indicate readiness for analysis
- Extract multiple facts from a single message if provided

Return your response as JSON:
{
  "reply": "Your next question or acknowledgment",
  "extractedFacts": {
    "issue": "...",
    "location": "...",
    "partyName": "...",
    "amount": "...",
    "dates": ["..."]
  },
  "chips": ["Yes", "No", "Not Sure"],
  "readyForAnalysis": false
}

Examples:

Example 1 - First message:
User: "My landlord is not returning my deposit"
You: {
  "reply": "I'm sorry to hear that. To help you, I need to understand your situation better. Which city are you in?",
  "extractedFacts": {"issue": "security deposit not returned", "location": null, "partyName": null, "amount": null, "dates": []},
  "chips": [],
  "readyForAnalysis": false
}

Example 2 - Follow-up:
User: "Bangalore"
You: {
  "reply": "Thank you. How much was the security deposit amount?",
  "extractedFacts": {"issue": "security deposit not returned", "location": "Bangalore", "partyName": null, "amount": null, "dates": []},
  "chips": [],
  "readyForAnalysis": false
}

Example 3 - Multiple facts:
User: "50000 rupees. I moved out 2 months ago."
You: {
  "reply": "Got it. And what is your landlord's name?",
  "extractedFacts": {"issue": "security deposit not returned", "location": "Bangalore", "partyName": null, "amount": "50000", "dates": ["2 months ago"]},
  "chips": [],
  "readyForAnalysis": false
}

Example 4 - Ready for analysis:
User: "Mr. Sharma"
You: {
  "reply": "Thank you for providing all this information. I now have a clear picture of your situation. Let me analyze the relevant laws for your case.",
  "extractedFacts": {"issue": "security deposit not returned", "location": "Bangalore", "partyName": "Mr. Sharma", "amount": "50000", "dates": ["2 months ago"]},
  "chips": [],
  "readyForAnalysis": true
}

Now process the actual conversation below."""


def get_bob_model():
    """Initialize IBM watsonx model for intake agent"""
    if not WATSONX_ENABLED:
        return None
    
    try:
        model = Model(
            model_id="meta-llama/llama-3-3-70b-instruct",
            params={
                GenParams.DECODING_METHOD: "greedy",
                GenParams.MAX_NEW_TOKENS: 300,
                GenParams.MIN_NEW_TOKENS: 50,
                GenParams.TEMPERATURE: 0.7,
                GenParams.TOP_K: 50,
                GenParams.TOP_P: 1
            },
            credentials={
                "apikey": WATSONX_API_KEY,
                "url": WATSONX_URL
            },
            project_id=WATSONX_PROJECT_ID
        )
        return model
    except Exception as e:
        print(f"Error initializing watsonx model: {e}")
        return None


def extract_facts_with_regex(message: str, current_facts: dict) -> dict:
    """
    Fallback fact extraction using regex patterns
    Used when IBM Bob is not available
    """
    facts = current_facts.copy()
    message_lower = message.lower()
    
    # Extract location (Indian cities)
    cities = ["bangalore", "bengaluru", "mumbai", "delhi", "pune", "hyderabad",
              "chennai", "kolkata", "ahmedabad", "jaipur", "lucknow", "kanpur"]
    for city in cities:
        if city in message_lower:
            facts["location"] = city.capitalize()
            if city == "bengaluru":
                facts["location"] = "Bangalore"
            break
    
    # Extract amount
    amount_patterns = [
        r'₹\s*(\d+(?:,\d+)*)',
        r'rs\.?\s*(\d+(?:,\d+)*)',
        r'rupees?\s*(\d+(?:,\d+)*)',
        r'(\d+(?:,\d+)*)\s*rupees?'
    ]
    for pattern in amount_patterns:
        match = re.search(pattern, message_lower)
        if match:
            facts["amount"] = match.group(1).replace(',', '')
            break
    
    # Extract dates
    date_patterns = [
        r'(\d+)\s+(?:months?|weeks?|days?)\s+ago',
        r'(?:on|in)\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)'
    ]
    dates = facts.get("dates", [])
    for pattern in date_patterns:
        matches = re.findall(pattern, message_lower)
        dates.extend(matches)
    if dates:
        facts["dates"] = list(set(dates))  # Remove duplicates
    
    # Extract issue keywords
    issue_keywords = {
        "deposit": "security deposit not returned",
        "salary": "salary not paid",
        "wages": "wages not paid",
        "defective": "defective product",
        "fraud": "consumer fraud",
        "termination": "wrongful termination",
        "eviction": "illegal eviction"
    }
    if not facts.get("issue"):
        for keyword, issue in issue_keywords.items():
            if keyword in message_lower:
                facts["issue"] = issue
                break
    
    return facts


def detect_emotional_language(message: str) -> bool:
    """Check if user is distressed"""
    emotional_keywords = [
        "stressed", "worried", "scared", "helpless", "frustrated",
        "angry", "upset", "desperate", "confused", "don't know what to do"
    ]
    return any(keyword in message.lower() for keyword in emotional_keywords)


async def process_intake(session: dict, user_message: str, formatted_history: str = "") -> dict:
    """
    Process user message during intake stage
    
    Uses IBM watsonx if available, falls back to regex-based extraction
    
    Args:
        session: Current session object
        user_message: User's latest message
        formatted_history: Formatted conversation history
        
    Returns:
        dict: Response with reply, extractedFacts, chips, readyForAnalysis
    """
    extracted_facts = session.get("extractedFacts", {
        "issue": None,
        "location": None,
        "partyName": None,
        "amount": None,
        "dates": []
    })
    
    # Try IBM Bob first
    if WATSONX_ENABLED:
        try:
            model = get_bob_model()
            if model:
                prompt = f"""{INTAKE_SYSTEM_PROMPT}

=== Current Session ===
Language: {session.get('language', 'en')}
State: {session.get('state', 'KA')}

{formatted_history}

=== User's Latest Message ===
{user_message}

=== Your Task ===
1. Update extractedFacts based on the user's message
2. Determine what critical information is still missing
3. Ask ONE clarifying question about the most important missing fact
4. If you have enough information (issue + location + 2 other facts), set readyForAnalysis to true

Respond ONLY with valid JSON. No other text."""

                response_text = model.generate_text(prompt=prompt)
                
                # Try to parse JSON response
                try:
                    # Extract JSON from response (in case there's extra text)
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        response = json.loads(json_match.group())
                        
                        # Merge extracted facts
                        merged_facts = {**extracted_facts, **response.get("extractedFacts", {})}
                        response["extractedFacts"] = merged_facts
                        
                        return response
                except json.JSONDecodeError:
                    print(f"Failed to parse Bob's response as JSON: {response_text}")
                    # Fall through to fallback
        except Exception as e:
            print(f"Error calling IBM Bob: {e}")
            # Fall through to fallback
    
    # Fallback: Rule-based extraction
    extracted_facts = extract_facts_with_regex(user_message, extracted_facts)
    
    # Generate appropriate response
    is_emotional = detect_emotional_language(user_message)
    empathy_prefix = "I understand this is a difficult situation. " if is_emotional else ""
    
    # Determine what to ask next
    if not extracted_facts.get("issue"):
        reply = f"{empathy_prefix}Could you briefly describe the legal issue you're facing?"
    elif not extracted_facts.get("location"):
        reply = "Which city are you in? This helps me find the right laws for your area."
    elif not extracted_facts.get("amount"):
        reply = "Is there any money involved in this matter? If so, how much?"
    elif not extracted_facts.get("dates") or len(extracted_facts.get("dates", [])) == 0:
        reply = "When did this happen? Please provide approximate dates."
    elif not extracted_facts.get("partyName"):
        reply = "What is the name of the other party (person or company)?"
    else:
        # Have enough facts
        reply = "Thank you for providing all this information. I now have a clear picture of your situation. Let me analyze the relevant laws for your case."
        return {
            "reply": reply,
            "extractedFacts": extracted_facts,
            "chips": [],
            "readyForAnalysis": True
        }
    
    return {
        "reply": reply,
        "extractedFacts": extracted_facts,
        "chips": [],
        "readyForAnalysis": False
    }


async def test_bob():
    """Test function to verify IBM Bob connection"""
    if not WATSONX_ENABLED:
        print("IBM watsonx is not configured. Set WATSONX_API_KEY and WATSONX_PROJECT_ID in .env file.")
        return
    
    model = get_bob_model()
    if not model:
        print("Failed to initialize IBM Bob model")
        return
    
    prompt = "You are a helpful legal assistant. Say hello in one sentence."
    
    try:
        response = model.generate_text(prompt=prompt)
        print(f"Bob says: {response}")
        return response
    except Exception as e:
        print(f"Error testing Bob: {e}")
        return None

# Made with Bob

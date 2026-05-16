"""
Classifier Agent for Court in Your Pocket
Classifies user's legal situation into categories using IBM watsonx AI
"""

import os
import json
import asyncio
from typing import Dict
from dotenv import load_dotenv
from ibm_watsonx_ai.foundation_models import ModelInference
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
from ibm_watsonx_ai import Credentials

# Load environment variables
load_dotenv()

# IBM watsonx credentials
IBM_WATSONX_API_KEY = os.getenv("IBM_WATSONX_API_KEY")
IBM_WATSONX_PROJECT_ID = os.getenv("IBM_WATSONX_PROJECT_ID")
IBM_WATSONX_URL = os.getenv("IBM_WATSONX_URL")

# Model configuration
MODEL_ID = "meta-llama/llama-3-3-70b-instruct"


def _initialize_watsonx_client():
    """Initialize IBM watsonx AI client"""
    credentials = Credentials(
        url=IBM_WATSONX_URL,
        api_key=IBM_WATSONX_API_KEY
    )
    return ModelInference(
        model_id=MODEL_ID,
        credentials=credentials,
        project_id=IBM_WATSONX_PROJECT_ID,
        params={
            GenParams.DECODING_METHOD: "greedy",
            GenParams.MAX_NEW_TOKENS: 300,
            GenParams.MIN_NEW_TOKENS: 10,
        }
    )


def _build_classification_prompt(facts: Dict) -> str:
    """Build cost-efficient classification prompt with Indian legal context"""
    
    issue = facts.get("issue", "Not specified")
    location = facts.get("location", "India")
    dates = facts.get("dates", [])
    amounts = facts.get("amounts", "Not specified")
    party_name = facts.get("partyName", "Not specified")
    
    # Format dates if provided
    dates_str = ", ".join(dates) if dates else "Not specified"
    
    prompt = f"""You are a legal classification assistant for Indian law. Analyze the user's situation and classify it into EXACTLY ONE category.

Categories:
- tenant: Issues related to rent, security deposits, eviction, landlord disputes under Indian tenancy laws (Model Tenancy Act 2021, state Rent Control Acts)
- employment: Wage disputes, wrongful termination, workplace issues under Indian labor laws (Code on Wages 2019, Industrial Disputes Act)
- consumer: Product defects, service failures, refunds under Consumer Protection Act 2019, RBI guidelines
- out_of_scope: Criminal matters, family law, property disputes, or anything outside the above three categories

Context: User is in {location}, India

Facts provided:
- Issue: {issue}
- Location: {location}
- Dates: {dates_str}
- Amounts: {amounts}
- Party Name: {party_name}

Return ONLY valid JSON in this exact format:
{{
  "category": "tenant|employment|consumer|out_of_scope",
  "sub_scenario": "brief_description_of_specific_issue"
}}

Examples:
- Security deposit not returned → {{"category": "tenant", "sub_scenario": "security_deposit_not_returned"}}
- Salary not paid → {{"category": "employment", "sub_scenario": "wage_non_payment"}}
- Defective product → {{"category": "consumer", "sub_scenario": "product_defect"}}
- Divorce case → {{"category": "out_of_scope", "sub_scenario": "family_law"}}

JSON Response:"""
    
    return prompt


def _parse_classification_response(response_text: str) -> Dict:
    """Parse Bob's response and extract JSON classification"""
    try:
        # Clean the response text
        response_text = response_text.strip()
        
        # Try to find JSON in the response
        if "{" in response_text and "}" in response_text:
            start_idx = response_text.find("{")
            end_idx = response_text.rfind("}") + 1
            json_str = response_text[start_idx:end_idx]
            
            # Parse JSON
            result = json.loads(json_str)
            
            # Validate required fields
            if "category" in result and "sub_scenario" in result:
                # Validate category is one of the allowed values
                valid_categories = ["tenant", "employment", "consumer", "out_of_scope"]
                if result["category"] in valid_categories:
                    return result
        
        # If parsing fails or validation fails, return fallback
        print(f"Warning: Failed to parse classification response: {response_text}")
        return {"category": "out_of_scope", "sub_scenario": "unknown"}
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return {"category": "out_of_scope", "sub_scenario": "unknown"}
    except Exception as e:
        print(f"Unexpected error parsing classification: {e}")
        return {"category": "out_of_scope", "sub_scenario": "unknown"}


async def classify_issue(facts: Dict) -> Dict:
    """
    Classify user's legal situation into categories using IBM watsonx AI
    
    Args:
        facts: Dictionary containing:
            - issue: Description of the legal issue
            - location: User's location (state in India)
            - dates: List of relevant dates
            - amounts: Monetary amounts involved
            - partyName: Name of the other party
    
    Returns:
        Dictionary with:
            - category: One of "tenant", "employment", "consumer", "out_of_scope"
            - sub_scenario: Brief description of the specific issue
    
    Example:
        >>> facts = {
        ...     "issue": "Landlord not returning security deposit",
        ...     "location": "Karnataka",
        ...     "dates": ["2024-01-15"],
        ...     "amounts": "₹40,000",
        ...     "partyName": "Mr. Sharma"
        ... }
        >>> result = await classify_issue(facts)
        >>> print(result)
        {"category": "tenant", "sub_scenario": "security_deposit_not_returned"}
    """
    try:
        # Initialize watsonx client
        client = _initialize_watsonx_client()
        
        # Build prompt
        prompt = _build_classification_prompt(facts)
        
        # Generate response
        response = client.generate_text(prompt=prompt)
        
        # Handle response type - convert to string if needed
        if isinstance(response, str):
            response_text = response
        elif isinstance(response, dict):
            response_text = response.get("generated_text", str(response))
        elif isinstance(response, list):
            response_text = str(response[0]) if response else ""
        else:
            response_text = str(response)
        
        # Parse and return classification
        classification = _parse_classification_response(response_text)
        
        print(f"Classification result: {classification}")
        return classification
        
    except Exception as e:
        print(f"Error in classify_issue: {e}")
        # Return safe fallback on any error
        return {"category": "out_of_scope", "sub_scenario": "unknown"}


# Test block
if __name__ == "__main__":
    print("=" * 60)
    print("Testing Classifier Agent with IBM watsonx AI")
    print("=" * 60)
    
    # Test case 1: Tenant issue - security deposit
    test_facts_1 = {
        "issue": "My landlord is not returning my security deposit of ₹40,000. I moved out 6 weeks ago and he is not responding to my calls.",
        "location": "Karnataka",
        "dates": ["2024-03-01"],
        "amounts": "₹40,000",
        "partyName": "Mr. Rajesh Kumar"
    }
    
    print("\nTest Case 1: Tenant Issue (Security Deposit)")
    print("-" * 60)
    print(f"Input facts: {json.dumps(test_facts_1, indent=2)}")
    result_1 = asyncio.run(classify_issue(test_facts_1))
    print(f"\nClassification Result:")
    print(json.dumps(result_1, indent=2))
    
    # Test case 2: Employment issue - wage dispute
    test_facts_2 = {
        "issue": "My employer has not paid my salary for the last 2 months",
        "location": "Maharashtra",
        "dates": ["2024-02-01", "2024-03-01"],
        "amounts": "₹60,000",
        "partyName": "ABC Technologies Pvt Ltd"
    }
    
    print("\n" + "=" * 60)
    print("Test Case 2: Employment Issue (Wage Non-payment)")
    print("-" * 60)
    print(f"Input facts: {json.dumps(test_facts_2, indent=2)}")
    result_2 = asyncio.run(classify_issue(test_facts_2))
    print(f"\nClassification Result:")
    print(json.dumps(result_2, indent=2))
    
    # Test case 3: Consumer issue - defective product
    test_facts_3 = {
        "issue": "I bought a refrigerator that stopped working after 1 week. The company is refusing to replace or refund.",
        "location": "Delhi",
        "dates": ["2024-04-01"],
        "amounts": "₹35,000",
        "partyName": "XYZ Electronics"
    }
    
    print("\n" + "=" * 60)
    print("Test Case 3: Consumer Issue (Defective Product)")
    print("-" * 60)
    print(f"Input facts: {json.dumps(test_facts_3, indent=2)}")
    result_3 = asyncio.run(classify_issue(test_facts_3))
    print(f"\nClassification Result:")
    print(json.dumps(result_3, indent=2))
    
    # Test case 4: Out of scope - criminal matter
    test_facts_4 = {
        "issue": "Someone stole my bike from the parking lot",
        "location": "Karnataka",
        "dates": ["2024-04-10"],
        "amounts": "₹80,000",
        "partyName": "Unknown"
    }
    
    print("\n" + "=" * 60)
    print("Test Case 4: Out of Scope (Criminal Matter)")
    print("-" * 60)
    print(f"Input facts: {json.dumps(test_facts_4, indent=2)}")
    result_4 = asyncio.run(classify_issue(test_facts_4))
    print(f"\nClassification Result:")
    print(json.dumps(result_4, indent=2))
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)

# Made with Bob

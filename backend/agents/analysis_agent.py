"""
Analysis Agent for Court in Your Pocket
Analyzes user rights based on facts and Indian law entries using IBM watsonx AI
"""

import os
import json
import asyncio
from typing import Dict, List
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
            GenParams.MAX_NEW_TOKENS: 800,
            GenParams.MIN_NEW_TOKENS: 10,
        }
    )


def _format_facts(facts: Dict) -> str:
    """Format facts dictionary into readable text"""
    formatted = []
    for key, value in facts.items():
        if value:
            if isinstance(value, list):
                formatted.append(f"- {key.replace('_', ' ').title()}: {', '.join(str(v) for v in value)}")
            else:
                formatted.append(f"- {key.replace('_', ' ').title()}: {value}")
    return "\n".join(formatted)


def _format_law_entries(law_entries: List[Dict]) -> str:
    """Format law entries into readable text for the prompt"""
    if not law_entries:
        return "No specific laws provided."
    
    formatted = []
    for idx, law in enumerate(law_entries, 1):
        entry = f"\nLaw Entry {idx}:"
        entry += f"\n- Law Name: {law.get('law_name', 'Unknown')}"
        entry += f"\n- Year: {law.get('year', 'Unknown')}"
        entry += f"\n- Section: {law.get('section', 'Unknown')}"
        entry += f"\n- Plain English: {law.get('plain_english', 'Not provided')}"
        entry += f"\n- Exact Quote: {law.get('exact_quote', 'Not provided')}"
        entry += f"\n- User Rights: {', '.join(law.get('user_rights', []))}"
        entry += f"\n- Deadline Days: {law.get('deadline_days', 'Not specified')}"
        entry += f"\n- Last Verified: {law.get('last_verified', 'Unknown')}"
        entry += f"\n- Source URL: {law.get('source_url', 'Not provided')}"
        formatted.append(entry)
    
    return "\n".join(formatted)


LANGUAGE_NAMES = {
    "en": "English", "hi": "Hindi", "ta": "Tamil",
    "te": "Telugu", "kn": "Kannada", "mr": "Marathi", "bn": "Bengali"
}


def _build_analysis_prompt(facts: Dict, law_entries: List[Dict], language="en") -> str:
    """Build detailed analysis prompt with Indian legal context"""
    
    language_name = LANGUAGE_NAMES.get(language, "English")
    formatted_facts = _format_facts(facts)
    formatted_laws = _format_law_entries(law_entries)
    
    prompt = f"""You are a legal rights analyst for Indian law. Your role is to explain user rights based ONLY on the provided Indian statutes.

CRITICAL RULES:
1. NEVER invent or assume laws not provided in the law_entries below
2. ONLY cite sections explicitly mentioned in the provided data
3. Use plain {language_name} suitable for non-lawyers in India
4. Provide confidence score 1-5 based on how well the facts match the law
5. Calculate realistic deadline in days based on Indian legal timelines

User Facts:
{formatted_facts}

Provided Indian Laws (USE ONLY THESE):
{formatted_laws}

Your task:
1. Match the user's situation to the most relevant provided laws
2. Explain their rights in simple, clear {language_name} suitable for non-lawyers in India
3. Quote the EXACT section text from the provided data
4. Assign confidence: 5=perfect match, 4=strong match, 3=moderate, 2=weak, 1=very uncertain
5. Estimate deadline based on typical Indian legal procedures (e.g., consumer complaints: 30-90 days, rent disputes: 60-180 days)

Return ONLY valid JSON in this exact format:
{{
  "rights": [
    {{
      "law_name": "exact name from provided data",
      "section": "exact section from provided data",
      "plain_english": "simple explanation in Indian English context",
      "exact_quote": "verbatim quote from provided law text",
      "confidence": 1-5,
      "last_verified": "date from provided data",
      "source_url": "URL from provided data"
    }}
  ],
  "confidence": 1-5,
  "deadline": number_of_days
}}

If no laws match well, return confidence 2 and explain limitations honestly.

JSON Response:"""
    
    return prompt


def _parse_analysis_response(response_text: str) -> Dict:
    """Parse Bob's response and extract JSON analysis"""
    try:
        # Clean the response text
        response_text = response_text.strip()
        
        # Try to find JSON in the response
        if "{" in response_text and "}" in response_text:
            start_idx = response_text.find("{")
            # Find the matching closing brace for the first opening brace
            depth = 0
            end_idx = start_idx
            for i, ch in enumerate(response_text[start_idx:], start=start_idx):
                if ch == "{":
                    depth += 1
                elif ch == "}":
                    depth -= 1
                    if depth == 0:
                        end_idx = i + 1
                        break
            json_str = response_text[start_idx:end_idx]
            
            # Parse JSON
            result = json.loads(json_str)
            
            # Validate required fields
            if "rights" in result and "confidence" in result and "deadline" in result:
                # Validate rights is a list
                if isinstance(result["rights"], list):
                    # Validate each right has required fields
                    for right in result["rights"]:
                        required_fields = ["law_name", "section", "plain_english", "exact_quote", 
                                         "confidence", "last_verified", "source_url"]
                        if all(field in right for field in required_fields):
                            continue
                        else:
                            raise ValueError("Missing required fields in rights entry")
                    
                    return result
        
        # If parsing fails, raise exception to trigger fallback
        raise ValueError("Failed to parse valid JSON response")
        
    except Exception as e:
        print(f"Error parsing analysis response: {e}")
        raise


def _create_fallback_response(law_entries: List[Dict]) -> Dict:
    """Create fallback response by formatting law_entries directly"""
    if not law_entries:
        return {
            "rights": [],
            "confidence": 2,
            "deadline": 30
        }
    
    rights = []
    for law in law_entries:
        right = {
            "law_name": law.get("law_name", "Unknown Law"),
            "section": law.get("section", "Section not specified"),
            "plain_english": law.get("plain_english", "Please refer to the exact legal text for details."),
            "exact_quote": law.get("exact_quote", "Quote not available"),
            "confidence": 3,  # Moderate confidence for fallback
            "last_verified": law.get("last_verified", "Unknown"),
            "source_url": law.get("source_url", "")
        }
        rights.append(right)
    
    # Calculate average deadline from law entries
    deadlines = [law.get("deadline_days", 30) for law in law_entries if law.get("deadline_days")]
    avg_deadline = sum(deadlines) // len(deadlines) if deadlines else 30
    
    return {
        "rights": rights,
        "confidence": 3,
        "deadline": avg_deadline
    }


async def analyze_rights(facts: Dict, law_entries: List[Dict], language="en") -> Dict:
    """
    Analyze user rights based on facts and Indian law entries using IBM watsonx AI
    
    Args:
        facts: Dictionary containing:
            - issue: Description of the legal issue
            - location: User's location (state in India)
            - dates: List of relevant dates
            - amounts: Monetary amounts involved
            - partyName: Name of the other party
        
        law_entries: List of law entry dictionaries from JSON knowledge base, each containing:
            - law_name: Name of the law
            - section: Section number
            - plain_english: Plain English explanation
            - exact_quote: Exact text from the law
            - deadline_days: Deadline in days
            - last_verified: Last verification date
            - source_url: Official source URL
        
        language: Language code for response (default: "en")
    
    Returns:
        Dictionary with:
            - rights: List of rights with law citations
            - confidence: Overall confidence score (1-5)
            - deadline: Deadline in days
    
    Example:
        >>> facts = {
        ...     "issue": "Landlord not returning security deposit",
        ...     "location": "Karnataka",
        ...     "dates": ["2024-01-15"],
        ...     "amounts": "₹40,000",
        ...     "partyName": "Mr. Sharma"
        ... }
        >>> law_entries = [{
        ...     "law_name": "Model Tenancy Act 2021",
        ...     "section": "Section 11",
        ...     "plain_english": "Landlord must return deposit within 1 month",
        ...     "exact_quote": "The landlord shall refund the security deposit...",
        ...     "deadline_days": 90,
        ...     "last_verified": "2026-05-01",
        ...     "source_url": "https://indiacode.nic.in/..."
        ... }]
        >>> result = await analyze_rights(facts, law_entries)
    """
    try:
        # Initialize watsonx client
        client = _initialize_watsonx_client()
        
        # Build prompt
        prompt = _build_analysis_prompt(facts, law_entries, language)
        
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
        
        # Try to parse the response
        try:
            analysis = _parse_analysis_response(response_text)
            return analysis
        except Exception as parse_error:
            # Use fallback - format law_entries directly
            fallback = _create_fallback_response(law_entries)
            return fallback
        
    except Exception as e:
        # Return fallback on any error
        fallback = _create_fallback_response(law_entries)
        return fallback


# Test block
if __name__ == "__main__":
    print("=" * 80)
    print("Testing Analysis Agent with IBM watsonx AI")
    print("=" * 80)
    
    # Test case 1: Tenant issue - security deposit not returned
    test_facts_1 = {
        "issue": "My landlord is not returning my security deposit of ₹40,000. I moved out 6 weeks ago after completing my 11-month rental agreement. The flat was in good condition.",
        "location": "Karnataka",
        "dates": ["2024-03-01"],
        "amounts": "₹40,000",
        "partyName": "Mr. Rajesh Kumar"
    }
    
    test_law_entries_1 = [
        {
            "id": "TN_IN_001",
            "category": "tenant",
            "scenario": "security_deposit_not_returned",
            "law_name": "Model Tenancy Act 2021",
            "year": 2021,
            "section": "Section 11",
            "plain_english": "The landlord must return the security deposit to the tenant within one month of the tenant vacating the premises, after deducting any legitimate dues.",
            "exact_quote": "The landlord shall refund the security deposit to the tenant within a period of one month from the date of handing over possession of the premises by the tenant, after deducting any amount that may be due from the tenant.",
            "user_rights": [
                "Right to receive full security deposit back within 1 month",
                "Right to receive written explanation for any deductions",
                "Right to file complaint with Rent Authority if not returned"
            ],
            "deadline_days": 90,
            "last_verified": "2026-05-01",
            "source_url": "https://indiacode.nic.in/handle/123456789/2032"
        }
    ]
    
    print("\nTest Case 1: Tenant Issue - Security Deposit Not Returned")
    print("-" * 80)
    print(f"Input facts:\n{json.dumps(test_facts_1, indent=2)}")
    print(f"\nProvided law entries:\n{json.dumps(test_law_entries_1, indent=2)}")
    result_1 = asyncio.run(analyze_rights(test_facts_1, test_law_entries_1))
    print(f"\nAnalysis Result:")
    print(json.dumps(result_1, indent=2))
    
    # Test case 2: Employment issue - wage non-payment
    test_facts_2 = {
        "issue": "My employer has not paid my salary for the last 2 months. I work as a software developer and my monthly salary is ₹30,000.",
        "location": "Maharashtra",
        "dates": ["2024-02-01", "2024-03-01"],
        "amounts": "₹60,000",
        "partyName": "ABC Technologies Pvt Ltd"
    }
    
    test_law_entries_2 = [
        {
            "id": "EMP_IN_001",
            "category": "employment",
            "scenario": "wage_non_payment",
            "law_name": "Code on Wages 2019",
            "year": 2019,
            "section": "Section 3 and Section 5",
            "plain_english": "Every employer must pay wages to employees on time (within 7 days for establishments with less than 1000 employees, within 10 days for larger ones). Delayed payment attracts compensation.",
            "exact_quote": "The wages of every person employed shall be paid before the expiry of the seventh day of the last day of the wage period in respect of which the wages are payable.",
            "user_rights": [
                "Right to receive wages on time",
                "Right to compensation for delayed payment",
                "Right to file complaint with Labour Commissioner"
            ],
            "deadline_days": 60,
            "last_verified": "2026-04-15",
            "source_url": "https://labour.gov.in/code-wages-2019"
        }
    ]
    
    print("\n" + "=" * 80)
    print("Test Case 2: Employment Issue - Wage Non-payment")
    print("-" * 80)
    print(f"Input facts:\n{json.dumps(test_facts_2, indent=2)}")
    print(f"\nProvided law entries:\n{json.dumps(test_law_entries_2, indent=2)}")
    result_2 = asyncio.run(analyze_rights(test_facts_2, test_law_entries_2))
    print(f"\nAnalysis Result:")
    print(json.dumps(result_2, indent=2))
    
    # Test case 3: Consumer issue - defective product
    test_facts_3 = {
        "issue": "I bought a refrigerator for ₹35,000 that stopped working after just 1 week. The company is refusing to replace or refund despite valid warranty.",
        "location": "Delhi",
        "dates": ["2024-04-01"],
        "amounts": "₹35,000",
        "partyName": "XYZ Electronics"
    }
    
    test_law_entries_3 = [
        {
            "id": "CON_IN_001",
            "category": "consumer",
            "scenario": "defective_product",
            "law_name": "Consumer Protection Act 2019",
            "year": 2019,
            "section": "Section 2(7) and Section 18",
            "plain_english": "Consumers have the right to seek replacement, refund, or compensation for defective goods. Manufacturers and sellers are liable for product defects.",
            "exact_quote": "A consumer has the right to be protected against marketing of goods and services which are hazardous to life and property, and the right to seek redressal against unfair trade practices.",
            "user_rights": [
                "Right to replacement of defective product",
                "Right to full refund if replacement not possible",
                "Right to compensation for any loss or damage",
                "Right to file complaint with Consumer Forum"
            ],
            "deadline_days": 30,
            "last_verified": "2026-05-10",
            "source_url": "https://consumeraffairs.nic.in/acts-and-rules"
        }
    ]
    
    print("\n" + "=" * 80)
    print("Test Case 3: Consumer Issue - Defective Product")
    print("-" * 80)
    print(f"Input facts:\n{json.dumps(test_facts_3, indent=2)}")
    print(f"\nProvided law entries:\n{json.dumps(test_law_entries_3, indent=2)}")
    result_3 = asyncio.run(analyze_rights(test_facts_3, test_law_entries_3))
    print(f"\nAnalysis Result:")
    print(json.dumps(result_3, indent=2))
    
    # Test case 4: Empty law entries (fallback test)
    test_facts_4 = {
        "issue": "Some legal issue",
        "location": "Karnataka",
        "dates": [],
        "amounts": "₹10,000",
        "partyName": "Someone"
    }
    
    print("\n" + "=" * 80)
    print("Test Case 4: Fallback Test - Empty Law Entries")
    print("-" * 80)
    print(f"Input facts:\n{json.dumps(test_facts_4, indent=2)}")
    print(f"\nProvided law entries: []")
    result_4 = asyncio.run(analyze_rights(test_facts_4, []))
    print(f"\nAnalysis Result (should use fallback):")
    print(json.dumps(result_4, indent=2))
    
    print("\n" + "=" * 80)
    print("All tests completed!")
    print("=" * 80)

# Made with Bob

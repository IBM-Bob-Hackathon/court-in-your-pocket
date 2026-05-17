import os
from typing import Dict, List, Optional, TYPE_CHECKING
from openai import OpenAI
from pydantic import BaseModel
import httpx

# Import session store
from session import session_store



# ============================================================================
# Pydantic Models for Structured Outputs
# ============================================================================

class ActionStep(BaseModel):
    """Represents a single step in an action plan."""
    step_number: int
    instruction: str
    time_estimate: str


class ActionPlanResponse(BaseModel):
    """Structured response from OpenAI for action plan generation."""
    steps: List[ActionStep]


# ============================================================================
# Session Data Retrieval
# ============================================================================

def get_session_data(session_id: str) -> Optional[Dict]:
    """
    Fetch session data from the session store.
    
    Retrieves:
    - extractedFacts: Dictionary of user-provided information
    - category: Legal category for the issue
    - Other session metadata
    
    Args:
        session_id: Unique identifier for the user session
        
    Returns:
        Dictionary containing session data or None if not found/expired
    """
    return session_store.get_session(session_id)


# ============================================================================
# Action Plan Agent (LLM-based)
# ============================================================================

class ActionPlanAgent:
    """
    Agent responsible for generating step-by-step action plans using OpenAI's LLM.
    Uses structured outputs to ensure consistent response format.
    """
    
    def __init__(self):
        """Initialize the OpenAI client with IBM API key from environment."""
        self.client: Optional[OpenAI] = None
        self.model = "meta-llama/llama-3-3-70b-instruct"  # Model that supports structured outputs
    
    def _ensure_client(self) -> OpenAI:
        """Lazy initialization of OpenAI client with IBM watsonx.ai configuration."""
        if self.client is None:
            api_key = os.getenv("IBM_WATSONX_API_KEY")
            base_url = os.getenv("IBM_WATSONX_URL")
            project_id = os.getenv("IBM_WATSONX_PROJECT_ID")
            
            if not api_key:
                raise ValueError("IBM_WATSONX_API_KEY environment variable not set. Please set it in your .env file or environment.")
            if not base_url:
                raise ValueError("IBM_WATSONX_URL environment variable not set. Please set it in your .env file or environment.")
            if not project_id:
                raise ValueError("IBM_WATSONX_PROJECT_ID environment variable not set. Please set it in your .env file or environment.")
            
            # Ensure base_url has the correct endpoint for OpenAI-compatible API
            # IBM watsonx.ai OpenAI-compatible endpoint is /ml/v1
            if not base_url.endswith('/ml/v1'):
                base_url = base_url.rstrip('/') + '/ml/v1'
            
            print(f"[ACTION_PLAN] Initializing OpenAI client with base_url: {base_url}")
            print(f"[ACTION_PLAN] Project ID: {project_id}")
            
            # Create a custom HTTP client without proxy support
            http_client = httpx.Client(
                timeout=60.0,
                follow_redirects=True
            )
            
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url,
                default_headers={
                    "X-Project-Id": project_id
                },
                http_client=http_client
            )
            print(f"[ACTION_PLAN] OpenAI client initialized successfully")
        return self.client
    
    def generate_action_plan(
        self,
        session_id: str,
        category: str,
        sub_scenario: str,
        option: str,
        extracted_facts: Optional[Dict] = None
    ) -> ActionPlanResponse:
        """
        Generate a step-by-step action plan using OpenAI's structured outputs.
        
        Args:
            session_id: Unique session identifier to fetch user data
            category: Legal category (e.g., "Tenant Rights")
            sub_scenario: Specific scenario (e.g., "Security Deposit Not Returned")
            option: User's chosen action - "A" (Demand Letter), "B" (File Complaint),
                   or "C" (Free Legal Aid)
            extracted_facts: Optional dictionary of user-specific facts for context
                           (if not provided, will be fetched from session)
            
        Returns:
            ActionPlanResponse containing 4-5 actionable steps with time estimates
        """
        
        # Fetch session data if extracted_facts not provided
        if extracted_facts is None:
            session_data = get_session_data(session_id)
            if session_data:
                extracted_facts = session_data.get("extractedFacts", {})
            else:
                extracted_facts = {}
        
        # Map option codes to human-readable actions
        option_map = {
            "A": "Demand Letter",
            "B": "File Complaint",
            "C": "Free Legal Aid"
        }
        
        chosen_action = option_map.get(option, option)
        
        # Build context from extracted facts if available
        context_info = ""
        if extracted_facts:
            context_info = "\n\nUser Context:\n"
            for key, value in extracted_facts.items():
                # Convert value to string and handle None values
                value_str = str(value) if value is not None else "Not provided"
                context_info += f"- {key.replace('_', ' ').title()}: {value_str}\n"
        
        # Construct the prompt
        system_prompt = """You are an expert legal assistant specializing in Indian law. 
Your task is to generate clear, actionable, step-by-step plans for users dealing with legal issues in India.
Be specific, practical, and ensure all advice is tailored to Indian legal procedures and jurisdiction."""
        
        user_prompt = f"""Generate a step-by-step action plan for an Indian user dealing with a {category} - {sub_scenario} issue, who chose option: {chosen_action}.

Requirements:
- Provide exactly 4-5 steps maximum
- Each step must be highly specific and actionable
- Include realistic time estimates for each step (e.g., "1-2 days", "1 week", "2-3 hours")
- Tailor all advice to Indian law, procedures, and jurisdiction
- Be practical and consider the user's context{context_info}

Focus on making the plan immediately actionable for someone in India."""
        
        try:
            # Ensure client is initialized
            client = self._ensure_client()
            project_id = os.getenv("IBM_WATSONX_PROJECT_ID")
            
            # Use structured outputs for consistent response format
            completion = client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                response_format=ActionPlanResponse,
                temperature=0.7,
                extra_body={
                    "project_id": project_id
                }
            )
            
            # Extract the parsed response
            action_plan = completion.choices[0].message.parsed
            if action_plan is None:
                raise Exception("Failed to parse action plan from OpenAI response")
            return action_plan
            
        except Exception as e:
            # Fallback error handling - avoid printing Unicode characters
            error_msg = str(e).encode('ascii', errors='replace').decode('ascii')
            print(f"[ACTION_PLAN] ERROR: {error_msg}")
            raise Exception(f"Failed to generate action plan: {error_msg}")


# ============================================================================
# Document Generator Service (Template-based)
# ============================================================================

class DocumentGenerator:
    """
    Service responsible for generating legal documents by replacing placeholders
    in templates with user-specific data from extractedFacts.
    """
    
    def __init__(self, templates_dir: str = "backend/templates"):
        """
        Initialize the document generator.
        
        Args:
            templates_dir: Directory containing document templates
        """
        self.templates_dir = templates_dir
    
    def get_template_path(self, category: Optional[str], option: str) -> str:
        """
        Determine the appropriate template file based on category and option.
        
        Args:
            category: Legal category (e.g., "Tenant Rights", "Consumer Protection", "Employment")
            option: User's chosen action ("A", "B", or "C")
            
        Returns:
            Path to the template file
        """
        # Map options to template types
        template_map = {
            "A": "demand_letter",
            "B": "complaint",
            "C": "legal_aid_application"
        }
        
        template_type = template_map.get(option, "demand_letter")
        
        # Map categories to template suffixes
        category_map = {
            "tenant": "tenant",
            "tenant rights": "tenant",
            "consumer": "consumer",
            "consumer protection": "consumer",
            "employment": "employment",
            "employment rights": "employment",
            "labor": "employment",
            "labour": "employment"
        }
        
        # Normalize category to find matching template
        # Handle None or empty category
        category_lower = (category or "").lower()
        category_suffix = None
        
        if category_lower:
            for key, suffix in category_map.items():
                if key in category_lower:
                    category_suffix = suffix
                    break
        
        # Default to tenant if no match found
        if not category_suffix:
            category_suffix = "tenant"
        
        # Construct template filename: template_{type}_{category}.txt
        template_filename = f"template_{template_type}_{category_suffix}.txt"
        template_path = os.path.join(self.templates_dir, template_filename)
        
        # Fallback to generic template if specific one doesn't exist
        if not os.path.exists(template_path):
            template_path = os.path.join(self.templates_dir, f"{template_type}_generic.txt")
        
        return template_path
    
    def load_template(self, template_path: str) -> str:
        """
        Load template content from file.
        
        Args:
            template_path: Path to the template file
            
        Returns:
            Template content as string
        """
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            # Return a basic fallback template
            return """Date: {{notice_date}}

To,
{{recipient_name}}
{{recipient_address}}

Subject: Formal Legal Notice

Dear Sir/Madam,

This is a formal notice regarding the matter of {{issue_description}}.

I request that you take appropriate action to resolve this matter within 15 days from the date of receipt of this letter.

Failure to comply will leave me with no option but to pursue legal remedies available under the law.

Yours sincerely,

{{sender_name}}
Contact: {{sender_contact}}
Email: {{sender_email}}

---
Note: This is a formal legal notice. Please retain a copy for your records."""
    
    def replace_placeholders(self, template: str, extracted_facts: Dict) -> str:
        """
        Replace all {{placeholder}} tokens in template with values from extractedFacts.
        
        Args:
            template: Template string containing {{placeholder}} tokens
            extracted_facts: Dictionary mapping placeholder names to values
            
        Returns:
            Document text with all placeholders replaced
        """
        from datetime import datetime
        import re
        
        document_text = template
        
        # Get user details with fallbacks
        user_name = (extracted_facts.get("user_name") or
                    extracted_facts.get("userName") or
                    extracted_facts.get("name") or
                    "")
        
        phone_number = (extracted_facts.get("phone_number") or
                       extracted_facts.get("phoneNumber") or
                       extracted_facts.get("contact") or
                       extracted_facts.get("phone") or
                       "")
        
        email_id = (extracted_facts.get("email_id") or
                   extracted_facts.get("emailId") or
                   extracted_facts.get("email") or
                   "")
        
        party_name = (extracted_facts.get("partyName") or
                     extracted_facts.get("party_name") or
                     "")
        
        location = (extracted_facts.get("location") or
                   extracted_facts.get("city") or
                   extracted_facts.get("address") or
                   "")
        
        amounts = extracted_facts.get("amounts") or extracted_facts.get("amount") or ""
        issue = extracted_facts.get("issue") or ""
        
        # Map extracted facts to template placeholders
        placeholder_mapping = {
            # Tenant-related mappings
            "landlord_name": party_name,
            "tenant_name": user_name,
            "tenant_contact": phone_number,
            "tenant_email": email_id,
            "property_address": location,
            "deposit_amount": amounts,
            "lease_start_date": extracted_facts.get("lease_start_date", ""),
            "lease_end_date": extracted_facts.get("lease_end_date", ""),
            "city": location,
            
            # Employment-related mappings
            "employer_name": party_name,
            "employee_name": user_name,
            "employee_contact": phone_number,
            "employee_email": email_id,
            "salary_amount": amounts,
            "employment_start_date": extracted_facts.get("employment_start_date", ""),
            "last_working_date": extracted_facts.get("last_working_date", ""),
            
            # Consumer-related mappings
            "seller_name": party_name,
            "consumer_name": user_name,
            "consumer_contact": phone_number,
            "consumer_email": email_id,
            "product_name": extracted_facts.get("product_name", ""),
            "purchase_amount": amounts,
            "purchase_date": extracted_facts.get("purchase_date", ""),
            
            # Generic mappings - these are the most important for the template
            "sender_name": user_name,
            "sender_contact": phone_number,
            "sender_email": email_id,
            "recipient_name": party_name,
            "recipient_address": location,
            "issue_description": issue,
            "amount": amounts,
        }
        
        # Add default values for common placeholders
        defaults = {
            "notice_date": datetime.now().strftime("%d/%m/%Y"),
            "deadline_days": "15",
        }
        
        # Merge: defaults < extracted_facts < placeholder_mapping
        all_facts = {**defaults, **extracted_facts, **placeholder_mapping}
        
        # Replace each placeholder with its corresponding value
        for key, value in all_facts.items():
            if value is not None and value != "" and value != []:
                # Handle list values (like dates)
                if isinstance(value, list):
                    value = ", ".join(str(v) for v in value if v)
                placeholder = f"{{{{{key}}}}}"  # {{key}}
                document_text = document_text.replace(placeholder, str(value))
        
        # Find any remaining unreplaced placeholders
        # For critical fields, provide better fallback messages
        remaining_placeholders = re.findall(r'\{\{(\w+)\}\}', document_text)
        for placeholder_name in remaining_placeholders:
            placeholder = f"{{{{{placeholder_name}}}}}"
            
            # Provide context-specific fallback messages
            if 'name' in placeholder_name.lower():
                replacement = "[Your Name]"
            elif 'contact' in placeholder_name.lower() or 'phone' in placeholder_name.lower():
                replacement = "[Your Contact Number]"
            elif 'email' in placeholder_name.lower():
                replacement = "[Your Email Address]"
            elif 'address' in placeholder_name.lower():
                replacement = "[Address]"
            elif 'amount' in placeholder_name.lower():
                replacement = "[Amount]"
            elif 'date' in placeholder_name.lower():
                replacement = "[Date]"
            else:
                replacement = f"[{placeholder_name.replace('_', ' ').title()}]"
            
            document_text = document_text.replace(placeholder, replacement)
        
        return document_text
    
    def generate_document(
        self,
        session_id: str,
        category: Optional[str] = None,
        option: Optional[str] = None
    ) -> str:
        """
        Generate a complete document by fetching session data and replacing template placeholders.
        
        Args:
            session_id: Unique identifier for the user session
            category: Optional category override (fetched from session if not provided)
            option: Optional option override (fetched from session if not provided)
            
        Returns:
            Complete document text with all placeholders replaced
        """
        # Fetch session data
        session_data = get_session_data(session_id)
        if not session_data:
            raise ValueError(f"Session not found: {session_id}")
        
        # Get extracted facts
        extracted_facts = session_data.get("extractedFacts", {}).copy()
        
        # IMPORTANT: Merge user details from userDetails field into extracted_facts
        # The user details (name, phone, email) are stored separately in the session
        user_details = session_data.get("userDetails", {})
        if user_details:
            print(f"[DOCUMENT_GEN] Found userDetails: {user_details}")
            # Add user details to extracted facts with priority
            extracted_facts.update({
                "user_name": user_details.get("user_name", extracted_facts.get("user_name", "")),
                "phone_number": user_details.get("phone_number", extracted_facts.get("phone_number", "")),
                "email_id": user_details.get("email_id", extracted_facts.get("email_id", "")),
            })
        else:
            print(f"[DOCUMENT_GEN] No userDetails found in session")
        
        # Print extracted_facts safely without Unicode characters
        try:
            facts_str = str(extracted_facts).encode('ascii', errors='replace').decode('ascii')
            print(f"[DOCUMENT_GEN] Final extracted_facts: {facts_str}")
        except Exception:
            print(f"[DOCUMENT_GEN] Final extracted_facts: <contains non-ASCII characters>")
        
        # Use provided values or fall back to session data
        # Handle None values properly
        session_category = session_data.get("category")
        session_option = session_data.get("option")
        
        category = category or session_category or "General"
        option = option or session_option or "A"
        
        # Load appropriate template
        template_path = self.get_template_path(category, option)
        template = self.load_template(template_path)
        
        # Replace placeholders
        document_text = self.replace_placeholders(template, extracted_facts)
        
        return document_text


# ============================================================================
# Singleton Instances
# ============================================================================

# Create singleton instances for use in API routes
action_plan_agent = ActionPlanAgent()
document_generator = DocumentGenerator()

# Made with Bob

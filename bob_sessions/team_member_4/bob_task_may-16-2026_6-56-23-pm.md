**User:**

<task>
def __init__(self):
        """Initialize the OpenAI client with API key from environment."""
        self.client: Optional[OpenAI] = None
        self.model = "gpt-4o-2024-08-06"  # Model that supports structured outputs
    
    def _ensure_client(self) -> OpenAI:
        """Lazy initialization of OpenAI client."""
        if self.client is None:
            api_key = os.getenv("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY environment variable not set. Please set it in your .env file or environment.")
            self.client = OpenAI(api_key=api_key)
        return self.client
 in this snippet I'm using the OpenAPI, but insted I need to use the IBM openAPI key
</task>
<environment_details>
# VSCode Visible Files
backend\agents\action_plan_agent.py

# VSCode Open Tabs
backend/routers/action_plan.py,backend/templates/demand_letter_generic.txt,backend/README.md,backend/requirements.txt,backend/agents/action_plan_agent.py,backend/.env.example,backend/main.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T13:25:57.312Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.00

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>advanced</slug>
<name>🛠️ Advanced</name>


# Current Workspace Directory (c:/SAI NAGENDRA/Projects/court-in-your-pocket) Files
backend/
backend/.env.example
backend/.gitignore
backend/main.py
backend/README.md
backend/requirements.txt
backend/agents/
backend/agents/action_plan_agent.py
backend/agents/README.md
backend/data/
backend/data/README.md
backend/routers/
backend/routers/action_plan.py
backend/routers/README.md
backend/templates/
backend/templates/demand_letter_generic.txt
backend/templates/README.md
docs/
docs/README.md
frontend/
frontend/.gitignore
frontend/eslint.config.js
frontend/index.html
frontend/package-lock.json
frontend/package.json
frontend/README.md
frontend/vite.config.js
frontend/public/
frontend/public/favicon.svg
frontend/public/icons.svg
frontend/src/
frontend/src/App.css
frontend/src/App.jsx
frontend/src/index.css
frontend/src/main.jsx
frontend/src/assets/
frontend/src/assets/hero.png
frontend/src/assets/react.svg
frontend/src/assets/vite.svg
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll help you update the code to use IBM's OpenAI-compatible API instead of OpenAI's API. First, let me read the current implementation to understand the full context.

<read_file>
<args>
  <file>
    <path>backend/agents/action_plan_agent.py</path>
  </file>
</args>
</read_file>

---

**User:**

[read_file for 'backend/agents/action_plan_agent.py'. Reading multiple files at once is more efficient for the LLM. If other files are relevant to your current task, please read them simultaneously.] Result:
<files>
<file><path>backend/agents/action_plan_agent.py</path>
<content lines="1-324">
  1 | import os
  2 | from typing import Dict, List, Optional, TYPE_CHECKING
  3 | from openai import OpenAI
  4 | from pydantic import BaseModel
  5 | 
  6 | if TYPE_CHECKING:
  7 |     from openai import OpenAI as OpenAIType
  8 | 
  9 | 
 10 | # ============================================================================
 11 | # Pydantic Models for Structured Outputs
 12 | # ============================================================================
 13 | 
 14 | class ActionStep(BaseModel):
 15 |     """Represents a single step in an action plan."""
 16 |     step_number: int
 17 |     instruction: str
 18 |     time_estimate: str
 19 | 
 20 | 
 21 | class ActionPlanResponse(BaseModel):
 22 |     """Structured response from OpenAI for action plan generation."""
 23 |     steps: List[ActionStep]
 24 | 
 25 | 
 26 | # ============================================================================
 27 | # Mock Session Data Store (In-Memory)
 28 | # ============================================================================
 29 | 
 30 | # Mock session storage - In production, replace with database queries
 31 | MOCK_SESSIONS = {
 32 |     "session_123": {
 33 |         "extractedFacts": {
 34 |             "landlord_name": "John Doe",
 35 |             "tenant_name": "Rajesh Kumar",
 36 |             "deposit_amount": "40000",
 37 |             "city": "Bangalore",
 38 |             "property_address": "123 MG Road, Bangalore",
 39 |             "lease_start_date": "01/01/2023",
 40 |             "lease_end_date": "31/12/2023",
 41 |             "notice_date": "15/01/2024"
 42 |         },
 43 |         "category": "Tenant Rights",
 44 |         "sub_scenario": "Security Deposit Not Returned",
 45 |         "option": "A"
 46 |     }
 47 | }
 48 | 
 49 | 
 50 | def get_session_data(session_id: str) -> Optional[Dict]:
 51 |     """
 52 |     Fetch session data from mock storage.
 53 |     
 54 |     In production, this would query your database to retrieve:
 55 |     - extractedFacts: Dictionary of user-provided information
 56 |     - category, sub_scenario, option: Context for the legal issue
 57 |     
 58 |     Args:
 59 |         session_id: Unique identifier for the user session
 60 |         
 61 |     Returns:
 62 |         Dictionary containing session data or None if not found
 63 |     """
 64 |     return MOCK_SESSIONS.get(session_id)
 65 | 
 66 | 
 67 | # ============================================================================
 68 | # Action Plan Agent (LLM-based)
 69 | # ============================================================================
 70 | 
 71 | class ActionPlanAgent:
 72 |     """
 73 |     Agent responsible for generating step-by-step action plans using OpenAI's LLM.
 74 |     Uses structured outputs to ensure consistent response format.
 75 |     """
 76 |     
 77 |     def __init__(self):
 78 |         """Initialize the OpenAI client with IBM API key from environment."""
 79 |         self.client: Optional[OpenAI] = None
 80 |         self.model = "gpt-4o-2024-08-06"  # Model that supports structured outputs
 81 |     
 82 |     def _ensure_client(self) -> OpenAI:
 83 |         """Lazy initialization of OpenAI client with IBM watsonx.ai configuration."""
 84 |         if self.client is None:
 85 |             api_key = os.getenv("IBM_API_KEY")
 86 |             base_url = os.getenv("IBM_BASE_URL")
 87 |             
 88 |             if not api_key:
 89 |                 raise ValueError("IBM_API_KEY environment variable not set. Please set it in your .env file or environment.")
 90 |             if not base_url:
 91 |                 raise ValueError("IBM_BASE_URL environment variable not set. Please set it in your .env file or environment.")
 92 |             
 93 |             self.client = OpenAI(
 94 |                 api_key=api_key,
 95 |                 base_url=base_url
 96 |             )
 97 |         return self.client
 98 |     
 99 |     def generate_action_plan(
100 |         self,
101 |         category: str,
102 |         sub_scenario: str,
103 |         option: str,
104 |         extracted_facts: Optional[Dict] = None
105 |     ) -> ActionPlanResponse:
106 |         """
107 |         Generate a step-by-step action plan using OpenAI's structured outputs.
108 |         
109 |         Args:
110 |             category: Legal category (e.g., "Tenant Rights")
111 |             sub_scenario: Specific scenario (e.g., "Security Deposit Not Returned")
112 |             option: User's chosen action - "A" (Demand Letter), "B" (File Complaint), 
113 |                    or "C" (Free Legal Aid)
114 |             extracted_facts: Optional dictionary of user-specific facts for context
115 |             
116 |         Returns:
117 |             ActionPlanResponse containing 4-5 actionable steps with time estimates
118 |         """
119 |         
120 |         # Map option codes to human-readable actions
121 |         option_map = {
122 |             "A": "Demand Letter",
123 |             "B": "File Complaint",
124 |             "C": "Free Legal Aid"
125 |         }
126 |         
127 |         chosen_action = option_map.get(option, option)
128 |         
129 |         # Build context from extracted facts if available
130 |         context_info = ""
131 |         if extracted_facts:
132 |             context_info = "\n\nUser Context:\n"
133 |             for key, value in extracted_facts.items():
134 |                 context_info += f"- {key.replace('_', ' ').title()}: {value}\n"
135 |         
136 |         # Construct the prompt
137 |         system_prompt = """You are an expert legal assistant specializing in Indian law. 
138 | Your task is to generate clear, actionable, step-by-step plans for users dealing with legal issues in India.
139 | Be specific, practical, and ensure all advice is tailored to Indian legal procedures and jurisdiction."""
140 |         
141 |         user_prompt = f"""Generate a step-by-step action plan for an Indian user dealing with a {category} - {sub_scenario} issue, who chose option: {chosen_action}.
142 | 
143 | Requirements:
144 | - Provide exactly 4-5 steps maximum
145 | - Each step must be highly specific and actionable
146 | - Include realistic time estimates for each step (e.g., "1-2 days", "1 week", "2-3 hours")
147 | - Tailor all advice to Indian law, procedures, and jurisdiction
148 | - Be practical and consider the user's context{context_info}
149 | 
150 | Focus on making the plan immediately actionable for someone in India."""
151 |         
152 |         try:
153 |             # Ensure client is initialized
154 |             client = self._ensure_client()
155 |             
156 |             # Use structured outputs for consistent response format
157 |             completion = client.beta.chat.completions.parse(
158 |                 model=self.model,
159 |                 messages=[
160 |                     {"role": "system", "content": system_prompt},
161 |                     {"role": "user", "content": user_prompt}
162 |                 ],
163 |                 response_format=ActionPlanResponse,
164 |                 temperature=0.7
165 |             )
166 |             
167 |             # Extract the parsed response
168 |             action_plan = completion.choices[0].message.parsed
169 |             if action_plan is None:
170 |                 raise Exception("Failed to parse action plan from OpenAI response")
171 |             return action_plan
172 |             
173 |         except Exception as e:
174 |             # Fallback error handling
175 |             raise Exception(f"Failed to generate action plan: {str(e)}")
176 | 
177 | 
178 | # ============================================================================
179 | # Document Generator Service (Template-based)
180 | # ============================================================================
181 | 
182 | class DocumentGenerator:
183 |     """
184 |     Service responsible for generating legal documents by replacing placeholders
185 |     in templates with user-specific data from extractedFacts.
186 |     """
187 |     
188 |     def __init__(self, templates_dir: str = "backend/templates"):
189 |         """
190 |         Initialize the document generator.
191 |         
192 |         Args:
193 |             templates_dir: Directory containing document templates
194 |         """
195 |         self.templates_dir = templates_dir
196 |     
197 |     def get_template_path(self, category: str, option: str) -> str:
198 |         """
199 |         Determine the appropriate template file based on category and option.
200 |         
201 |         Args:
202 |             category: Legal category (e.g., "Tenant Rights")
203 |             option: User's chosen action ("A", "B", or "C")
204 |             
205 |         Returns:
206 |             Path to the template file
207 |         """
208 |         # Map options to template types
209 |         template_map = {
210 |             "A": "demand_letter",
211 |             "B": "complaint",
212 |             "C": "legal_aid_application"
213 |         }
214 |         
215 |         template_type = template_map.get(option, "demand_letter")
216 |         
217 |         # Sanitize category for filename
218 |         category_slug = category.lower().replace(" ", "_")
219 |         
220 |         # Construct template filename
221 |         template_filename = f"{category_slug}_{template_type}.txt"
222 |         template_path = os.path.join(self.templates_dir, template_filename)
223 |         
224 |         # Fallback to generic template if specific one doesn't exist
225 |         if not os.path.exists(template_path):
226 |             template_path = os.path.join(self.templates_dir, f"{template_type}_generic.txt")
227 |         
228 |         return template_path
229 |     
230 |     def load_template(self, template_path: str) -> str:
231 |         """
232 |         Load template content from file.
233 |         
234 |         Args:
235 |             template_path: Path to the template file
236 |             
237 |         Returns:
238 |             Template content as string
239 |         """
240 |         try:
241 |             with open(template_path, 'r', encoding='utf-8') as f:
242 |                 return f.read()
243 |         except FileNotFoundError:
244 |             # Return a basic fallback template
245 |             return """Dear {{landlord_name}},
246 | 
247 | This is a formal notice regarding {{sub_scenario}}.
248 | 
249 | Details:
250 | {{details}}
251 | 
252 | Please respond within 15 days.
253 | 
254 | Sincerely,
255 | {{tenant_name}}"""
256 |     
257 |     def replace_placeholders(self, template: str, extracted_facts: Dict) -> str:
258 |         """
259 |         Replace all {{placeholder}} tokens in template with values from extractedFacts.
260 |         
261 |         Args:
262 |             template: Template string containing {{placeholder}} tokens
263 |             extracted_facts: Dictionary mapping placeholder names to values
264 |             
265 |         Returns:
266 |             Document text with all placeholders replaced
267 |         """
268 |         document_text = template
269 |         
270 |         # Replace each placeholder with its corresponding value
271 |         for key, value in extracted_facts.items():
272 |             placeholder = f"{{{{{key}}}}}"  # {{key}}
273 |             document_text = document_text.replace(placeholder, str(value))
274 |         
275 |         return document_text
276 |     
277 |     def generate_document(
278 |         self,
279 |         session_id: str,
280 |         category: Optional[str] = None,
281 |         option: Optional[str] = None
282 |     ) -> str:
283 |         """
284 |         Generate a complete document by fetching session data and replacing template placeholders.
285 |         
286 |         Args:
287 |             session_id: Unique identifier for the user session
288 |             category: Optional category override (fetched from session if not provided)
289 |             option: Optional option override (fetched from session if not provided)
290 |             
291 |         Returns:
292 |             Complete document text with all placeholders replaced
293 |         """
294 |         # Fetch session data
295 |         session_data = get_session_data(session_id)
296 |         if not session_data:
297 |             raise ValueError(f"Session not found: {session_id}")
298 |         
299 |         # Get extracted facts
300 |         extracted_facts = session_data.get("extractedFacts", {})
301 |         
302 |         # Use provided values or fall back to session data
303 |         category = category or session_data.get("category", "General")
304 |         option = option or session_data.get("option", "A")
305 |         
306 |         # Load appropriate template
307 |         template_path = self.get_template_path(category, option)
308 |         template = self.load_template(template_path)
309 |         
310 |         # Replace placeholders
311 |         document_text = self.replace_placeholders(template, extracted_facts)
312 |         
313 |         return document_text
314 | 
315 | 
316 | # ============================================================================
317 | # Singleton Instances
318 | # ============================================================================
319 | 
320 | # Create singleton instances for use in API routes
321 | action_plan_agent = ActionPlanAgent()
322 | document_generator = DocumentGenerator()
323 | 
324 | # Made with Bob
</content>
</file>
</files>
<environment_details>
# VSCode Visible Files
backend\agents\action_plan_agent.py

# VSCode Open Tabs
backend/routers/action_plan.py,backend/templates/demand_letter_generic.txt,backend/README.md,backend/requirements.txt,backend/agents/action_plan_agent.py,backend/.env.example,backend/main.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T13:26:10.378Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.04

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>advanced</slug>
<name>🛠️ Advanced</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I can see the code has already been updated to use IBM's API! Let me check the `.env.example` file to ensure the environment variables are properly documented:

<read_file>
<args>
  <file>
    <path>backend/.env.example</path>
  </file>
</args>
</read_file>

---

**User:**

[read_file for 'backend/.env.example'. Reading multiple files at once is more efficient for the LLM. If other files are relevant to your current task, please read them simultaneously.] Result:
<files>
<file><path>backend/.env.example</path>
<content lines="1-10">
 1 | # IBM watsonx.ai Configuration (OpenAI-compatible API)
 2 | IBM_API_KEY=your_ibm_api_key_here
 3 | IBM_BASE_URL=https://us-south.ml.cloud.ibm.com/ml/v1/text/chat/completions
 4 | 
 5 | # Server Configuration (Optional)
 6 | HOST=0.0.0.0
 7 | PORT=8000
 8 | 
 9 | # Environment
10 | ENVIRONMENT=development
</content>
</file>
</files>
<environment_details>
# VSCode Visible Files
backend\agents\action_plan_agent.py

# VSCode Open Tabs
backend/routers/action_plan.py,backend/templates/demand_letter_generic.txt,backend/README.md,backend/requirements.txt,backend/agents/action_plan_agent.py,backend/.env.example,backend/main.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T13:26:16.895Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.08

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>advanced</slug>
<name>🛠️ Advanced</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

<attempt_completion>
<result>
The code has already been updated to use IBM's OpenAI-compatible API. Here's what was changed:

**In [`action_plan_agent.py`](backend/agents/action_plan_agent.py:78-96):**
- Changed environment variable from `OPENAI_API_KEY` to `IBM_API_KEY`
- Added `IBM_BASE_URL` environment variable for IBM watsonx.ai endpoint
- Updated the OpenAI client initialization to use both `api_key` and `base_url` parameters
- Updated error messages to reference IBM credentials

**Configuration in [`.env.example`](backend/.env.example:1-3):**
- `IBM_API_KEY`: Your IBM API key
- `IBM_BASE_URL`: IBM watsonx.ai endpoint URL

The implementation uses the OpenAI Python SDK's compatibility with IBM watsonx.ai by configuring a custom `base_url`. You'll need to set these environment variables in your `.env` file to use IBM's API.
</result>
</attempt_completion>


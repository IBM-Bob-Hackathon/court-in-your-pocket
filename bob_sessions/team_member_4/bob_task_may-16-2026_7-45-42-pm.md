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
backend/routers/action_plan.py,backend/templates/demand_letter_generic.txt,backend/README.md,backend/requirements.txt,backend/agents/action_plan_agent.py,backend/.env.example,backend/.env,backend/main.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T13:19:40.901Z
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
<content lines="1-316">
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
 78 |         """Initialize the OpenAI client with API key from environment."""
 79 |         self.client: Optional[OpenAI] = None
 80 |         self.model = "gpt-4o-2024-08-06"  # Model that supports structured outputs
 81 |     
 82 |     def _ensure_client(self) -> OpenAI:
 83 |         """Lazy initialization of OpenAI client."""
 84 |         if self.client is None:
 85 |             api_key = os.getenv("OPENAI_API_KEY")
 86 |             if not api_key:
 87 |                 raise ValueError("OPENAI_API_KEY environment variable not set. Please set it in your .env file or environment.")
 88 |             self.client = OpenAI(api_key=api_key)
 89 |         return self.client
 90 |     
 91 |     def generate_action_plan(
 92 |         self,
 93 |         category: str,
 94 |         sub_scenario: str,
 95 |         option: str,
 96 |         extracted_facts: Optional[Dict] = None
 97 |     ) -> ActionPlanResponse:
 98 |         """
 99 |         Generate a step-by-step action plan using OpenAI's structured outputs.
100 |         
101 |         Args:
102 |             category: Legal category (e.g., "Tenant Rights")
103 |             sub_scenario: Specific scenario (e.g., "Security Deposit Not Returned")
104 |             option: User's chosen action - "A" (Demand Letter), "B" (File Complaint), 
105 |                    or "C" (Free Legal Aid)
106 |             extracted_facts: Optional dictionary of user-specific facts for context
107 |             
108 |         Returns:
109 |             ActionPlanResponse containing 4-5 actionable steps with time estimates
110 |         """
111 |         
112 |         # Map option codes to human-readable actions
113 |         option_map = {
114 |             "A": "Demand Letter",
115 |             "B": "File Complaint",
116 |             "C": "Free Legal Aid"
117 |         }
118 |         
119 |         chosen_action = option_map.get(option, option)
120 |         
121 |         # Build context from extracted facts if available
122 |         context_info = ""
123 |         if extracted_facts:
124 |             context_info = "\n\nUser Context:\n"
125 |             for key, value in extracted_facts.items():
126 |                 context_info += f"- {key.replace('_', ' ').title()}: {value}\n"
127 |         
128 |         # Construct the prompt
129 |         system_prompt = """You are an expert legal assistant specializing in Indian law. 
130 | Your task is to generate clear, actionable, step-by-step plans for users dealing with legal issues in India.
131 | Be specific, practical, and ensure all advice is tailored to Indian legal procedures and jurisdiction."""
132 |         
133 |         user_prompt = f"""Generate a step-by-step action plan for an Indian user dealing with a {category} - {sub_scenario} issue, who chose option: {chosen_action}.
134 | 
135 | Requirements:
136 | - Provide exactly 4-5 steps maximum
137 | - Each step must be highly specific and actionable
138 | - Include realistic time estimates for each step (e.g., "1-2 days", "1 week", "2-3 hours")
139 | - Tailor all advice to Indian law, procedures, and jurisdiction
140 | - Be practical and consider the user's context{context_info}
141 | 
142 | Focus on making the plan immediately actionable for someone in India."""
143 |         
144 |         try:
145 |             # Ensure client is initialized
146 |             client = self._ensure_client()
147 |             
148 |             # Use structured outputs for consistent response format
149 |             completion = client.beta.chat.completions.parse(
150 |                 model=self.model,
151 |                 messages=[
152 |                     {"role": "system", "content": system_prompt},
153 |                     {"role": "user", "content": user_prompt}
154 |                 ],
155 |                 response_format=ActionPlanResponse,
156 |                 temperature=0.7
157 |             )
158 |             
159 |             # Extract the parsed response
160 |             action_plan = completion.choices[0].message.parsed
161 |             if action_plan is None:
162 |                 raise Exception("Failed to parse action plan from OpenAI response")
163 |             return action_plan
164 |             
165 |         except Exception as e:
166 |             # Fallback error handling
167 |             raise Exception(f"Failed to generate action plan: {str(e)}")
168 | 
169 | 
170 | # ============================================================================
171 | # Document Generator Service (Template-based)
172 | # ============================================================================
173 | 
174 | class DocumentGenerator:
175 |     """
176 |     Service responsible for generating legal documents by replacing placeholders
177 |     in templates with user-specific data from extractedFacts.
178 |     """
179 |     
180 |     def __init__(self, templates_dir: str = "backend/templates"):
181 |         """
182 |         Initialize the document generator.
183 |         
184 |         Args:
185 |             templates_dir: Directory containing document templates
186 |         """
187 |         self.templates_dir = templates_dir
188 |     
189 |     def get_template_path(self, category: str, option: str) -> str:
190 |         """
191 |         Determine the appropriate template file based on category and option.
192 |         
193 |         Args:
194 |             category: Legal category (e.g., "Tenant Rights")
195 |             option: User's chosen action ("A", "B", or "C")
196 |             
197 |         Returns:
198 |             Path to the template file
199 |         """
200 |         # Map options to template types
201 |         template_map = {
202 |             "A": "demand_letter",
203 |             "B": "complaint",
204 |             "C": "legal_aid_application"
205 |         }
206 |         
207 |         template_type = template_map.get(option, "demand_letter")
208 |         
209 |         # Sanitize category for filename
210 |         category_slug = category.lower().replace(" ", "_")
211 |         
212 |         # Construct template filename
213 |         template_filename = f"{category_slug}_{template_type}.txt"
214 |         template_path = os.path.join(self.templates_dir, template_filename)
215 |         
216 |         # Fallback to generic template if specific one doesn't exist
217 |         if not os.path.exists(template_path):
218 |             template_path = os.path.join(self.templates_dir, f"{template_type}_generic.txt")
219 |         
220 |         return template_path
221 |     
222 |     def load_template(self, template_path: str) -> str:
223 |         """
224 |         Load template content from file.
225 |         
226 |         Args:
227 |             template_path: Path to the template file
228 |             
229 |         Returns:
230 |             Template content as string
231 |         """
232 |         try:
233 |             with open(template_path, 'r', encoding='utf-8') as f:
234 |                 return f.read()
235 |         except FileNotFoundError:
236 |             # Return a basic fallback template
237 |             return """Dear {{landlord_name}},
238 | 
239 | This is a formal notice regarding {{sub_scenario}}.
240 | 
241 | Details:
242 | {{details}}
243 | 
244 | Please respond within 15 days.
245 | 
246 | Sincerely,
247 | {{tenant_name}}"""
248 |     
249 |     def replace_placeholders(self, template: str, extracted_facts: Dict) -> str:
250 |         """
251 |         Replace all {{placeholder}} tokens in template with values from extractedFacts.
252 |         
253 |         Args:
254 |             template: Template string containing {{placeholder}} tokens
255 |             extracted_facts: Dictionary mapping placeholder names to values
256 |             
257 |         Returns:
258 |             Document text with all placeholders replaced
259 |         """
260 |         document_text = template
261 |         
262 |         # Replace each placeholder with its corresponding value
263 |         for key, value in extracted_facts.items():
264 |             placeholder = f"{{{{{key}}}}}"  # {{key}}
265 |             document_text = document_text.replace(placeholder, str(value))
266 |         
267 |         return document_text
268 |     
269 |     def generate_document(
270 |         self,
271 |         session_id: str,
272 |         category: Optional[str] = None,
273 |         option: Optional[str] = None
274 |     ) -> str:
275 |         """
276 |         Generate a complete document by fetching session data and replacing template placeholders.
277 |         
278 |         Args:
279 |             session_id: Unique identifier for the user session
280 |             category: Optional category override (fetched from session if not provided)
281 |             option: Optional option override (fetched from session if not provided)
282 |             
283 |         Returns:
284 |             Complete document text with all placeholders replaced
285 |         """
286 |         # Fetch session data
287 |         session_data = get_session_data(session_id)
288 |         if not session_data:
289 |             raise ValueError(f"Session not found: {session_id}")
290 |         
291 |         # Get extracted facts
292 |         extracted_facts = session_data.get("extractedFacts", {})
293 |         
294 |         # Use provided values or fall back to session data
295 |         category = category or session_data.get("category", "General")
296 |         option = option or session_data.get("option", "A")
297 |         
298 |         # Load appropriate template
299 |         template_path = self.get_template_path(category, option)
300 |         template = self.load_template(template_path)
301 |         
302 |         # Replace placeholders
303 |         document_text = self.replace_placeholders(template, extracted_facts)
304 |         
305 |         return document_text
306 | 
307 | 
308 | # ============================================================================
309 | # Singleton Instances
310 | # ============================================================================
311 | 
312 | # Create singleton instances for use in API routes
313 | action_plan_agent = ActionPlanAgent()
314 | document_generator = DocumentGenerator()
315 | 
316 | # Made with Bob
</content>
</file>
</files>
<environment_details>
# VSCode Visible Files
backend\agents\action_plan_agent.py

# VSCode Open Tabs
backend/routers/action_plan.py,backend/templates/demand_letter_generic.txt,backend/README.md,backend/requirements.txt,backend/agents/action_plan_agent.py,backend/.env.example,backend/.env,backend/main.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T13:19:52.446Z
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

I'll help you update the code to use IBM's OpenAI-compatible API. Let me also check the `.env.example` file to understand the current configuration structure.

<read_file>
<args>
  <file>
    <path>backend/.env.example</path>
  </file>
  <file>
    <path>backend/.env</path>
  </file>
</args>
</read_file>

---

**User:**

[read_file for 'backend/.env.example', 'backend/.env'] Result:
<files>
<file><path>backend/.env.example</path>
<content lines="1-9">
1 | # OpenAI Configuration
2 | OPENAI_API_KEY=FG93EZzNowH6ifwMTchJGfa_oFsQTGnIswM2SooparfB
3 | 
4 | # Server Configuration (Optional)
5 | HOST=0.0.0.0
6 | PORT=8000
7 | 
8 | # Environment
9 | ENVIRONMENT=development
</content>
</file>
<file><path>backend/.env</path>
<content lines="1-9">
1 | # OpenAI Configuration
2 | OPENAI_API_KEY=_jHZMIjQ3ajM6jxQJJe4LwixQ_WzMozQZzeS_UNEu6Rd
3 | 
4 | # Server Configuration (Optional)
5 | HOST=0.0.0.0
6 | PORT=8000
7 | 
8 | # Environment
9 | ENVIRONMENT=development
</content>
</file>
</files>
<environment_details>
# VSCode Visible Files
backend\agents\action_plan_agent.py

# VSCode Open Tabs
backend/routers/action_plan.py,backend/templates/demand_letter_generic.txt,backend/README.md,backend/requirements.txt,backend/agents/action_plan_agent.py,backend/.env.example,backend/.env,backend/main.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T13:20:03.466Z
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

Now I'll update the code to use IBM's OpenAI-compatible API. IBM's watsonx.ai provides an OpenAI-compatible API that requires a base URL and API key. I'll make the necessary changes:

<apply_diff>
<path>backend/agents/action_plan_agent.py</path>
<diff>
<<<<<<< SEARCH
:start_line:77
-------
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
=======
    def __init__(self):
        """Initialize the OpenAI client with IBM API key from environment."""
        self.client: Optional[OpenAI] = None
        self.model = "gpt-4o-2024-08-06"  # Model that supports structured outputs
    
    def _ensure_client(self) -> OpenAI:
        """Lazy initialization of OpenAI client with IBM watsonx.ai configuration."""
        if self.client is None:
            api_key = os.getenv("IBM_API_KEY")
            base_url = os.getenv("IBM_BASE_URL")
            
            if not api_key:
                raise ValueError("IBM_API_KEY environment variable not set. Please set it in your .env file or environment.")
            if not base_url:
                raise ValueError("IBM_BASE_URL environment variable not set. Please set it in your .env file or environment.")
            
            self.client = OpenAI(
                api_key=api_key,
                base_url=base_url
            )
        return self.client
>>>>>>> REPLACE
</diff>
</apply_diff>

---

**User:**

[apply_diff for 'backend/agents/action_plan_agent.py'] Result:
<file_write_result>
<path>backend/agents/action_plan_agent.py</path>
<operation>modified</operation>
<notice>
<i>You do not need to re-read the file, as you have seen all changes</i>
<i>Proceed with the task using these changes as the new baseline.</i>
</notice>
</file_write_result>

<notice>Making multiple related changes in a single apply_diff is more efficient. If other changes are needed in this file, please include them as additional SEARCH/REPLACE blocks.</notice>
<environment_details>
# VSCode Visible Files
backend\agents\action_plan_agent.py

# VSCode Open Tabs
backend/routers/action_plan.py,backend/agents/action_plan_agent.py,backend/templates/demand_letter_generic.txt,backend/README.md,backend/requirements.txt,backend/.env.example,backend/.env,backend/main.py

# Recently Modified Files
These files have been modified since you last accessed them (file was just edited so you may need to re-read it before editing):
backend/agents/action_plan_agent.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T13:20:20.272Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.13

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

Now I'll update the `.env.example` file to reflect the IBM API configuration:

<apply_diff>
<path>backend/.env.example</path>
<diff>
<<<<<<< SEARCH
:start_line:1
-------
# OpenAI Configuration
OPENAI_API_KEY=FG93EZzNowH6ifwMTchJGfa_oFsQTGnIswM2SooparfB
=======
# IBM watsonx.ai Configuration (OpenAI-compatible API)
IBM_API_KEY=your_ibm_api_key_here
IBM_BASE_URL=https://us-south.ml.cloud.ibm.com/ml/v1/text/chat/completions
>>>>>>> REPLACE
</diff>
</apply_diff>

---

**User:**

[apply_diff for 'backend/.env.example'] Result:
<file_write_result>
<path>backend/.env.example</path>
<operation>modified</operation>
<notice>
<i>You do not need to re-read the file, as you have seen all changes</i>
<i>Proceed with the task using these changes as the new baseline.</i>
</notice>
</file_write_result>

<notice>Making multiple related changes in a single apply_diff is more efficient. If other changes are needed in this file, please include them as additional SEARCH/REPLACE blocks.</notice>
<environment_details>
# VSCode Visible Files
backend\.env.example

# VSCode Open Tabs
backend/routers/action_plan.py,backend/agents/action_plan_agent.py,backend/.env.example,backend/templates/demand_letter_generic.txt,backend/README.md,backend/requirements.txt,backend/.env,backend/main.py

# Recently Modified Files
These files have been modified since you last accessed them (file was just edited so you may need to re-read it before editing):
backend/.env.example

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T13:20:38.062Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.18

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>advanced</slug>
<name>🛠️ Advanced</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>


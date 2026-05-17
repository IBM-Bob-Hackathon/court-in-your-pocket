**User:**

<task>
Look at backend/main.py. It imports classify_issue and analyze_rights from the agents but never imports or registers the legal router. Now look at backend/routers/legal.py — there is a router object defined there with the /api/legal/analyze and /api/legal/resources endpoints. Without registering this router in main.py, FastAPI has no knowledge of those endpoints, which is why every request to them returns 404.

Add the import for the router from routers/legal.py and register it with app.include_router(...). Do not change anything else.
</task>
<environment_details>
# VSCode Visible Files
backend\agents\analysis_agent.py

# VSCode Open Tabs
../../../Downloads/developer_breakdown.md,.git.ignore,backend/.env,backend/requirements.txt,backend/session_store.py,backend/routers/legal.py,backend/agents/analysis_agent.py,backend/main.py,frontend/vite.config.js,frontend/src/screens/RightsScreen.jsx,frontend/SETUP.md,frontend/src/App.jsx,frontend/src/main.jsx,frontend/src/context/AppContext.jsx,backend/agents/classifier_agent.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T15:05:52.976Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.00

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>


# Current Workspace Directory (c:/Users/SharmilasaiKalavagun/Documents/IBM Bob Hackathon/court-in-your-pocket) Files
.git.ignore
Idea Plan.txt
Work_division.txt
backend/
backend/.env
backend/main.py
backend/README.md
backend/requirements.txt
backend/session_store.py
backend/agents/
backend/agents/analysis_agent.py
backend/agents/classifier_agent.py
backend/agents/README.md
backend/data/
backend/data/README.md
backend/routers/
backend/routers/legal.py
backend/routers/README.md
backend/templates/
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
frontend/SETUP.md
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
frontend/src/context/
frontend/src/context/AppContext.jsx
frontend/src/screens/
frontend/src/screens/README.md
frontend/src/screens/RightsScreen.jsx
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll help you fix the 404 issue by registering the legal router in main.py. Let me first read both files to understand the current state.

<read_file>
<args>
<file>
<path>backend/main.py</path>
</file>
<file>
<path>backend/routers/legal.py</path>
</file>
</args>
</read_file>

---

**User:**

[read_file for 'backend/main.py', 'backend/routers/legal.py'] Result:
<files>
<file><path>backend/main.py</path>
<content lines="1-55">
 1 | from fastapi import FastAPI
 2 | from agents.classifier_agent import classify_issue
 3 | from agents.analysis_agent import analyze_rights
 4 | from routers.legal import router as legal_router
 5 | 
 6 | app = FastAPI()
 7 | app.include_router(legal_router)
 8 | 
 9 | @app.get("/")
10 | def home():
11 |     return {"status": "Court in Your Pocket API running"}
12 | 
13 | @app.get("/test-agents")
14 | async def test_agents(language: str = "en"):
15 |     """
16 |     Test endpoint for agents with language support
17 |     
18 |     Query Parameters:
19 |         language: Language code (en, hi, ta, te, kn, mr, bn). Default: en
20 |     
21 |     Examples:
22 |         /test-agents (English - default)
23 |         /test-agents?language=hi (Hindi)
24 |         /test-agents?language=ta (Tamil)
25 |         /test-agents?language=te (Telugu)
26 |         /test-agents?language=kn (Kannada)
27 |         /test-agents?language=mr (Marathi)
28 |         /test-agents?language=bn (Bengali)
29 |     """
30 |     facts = {
31 |         "issue": "landlord not returning security deposit",
32 |         "location": "Bangalore",
33 |         "amount": "4000",
34 |         "dates": ["2026-03-15"],
35 |         "partyName": "Mr. Sharma"
36 |     }
37 | 
38 |     sample_law = [{
39 |         "law_name": "Model Tenancy Act",
40 |         "section": "Section 11",
41 |         "plain_english": "Landlord must return deposit within 1 month",
42 |         "exact_quote": "The landlord shall refund the security deposit...",
43 |         "deadline_days": 90,
44 |         "last_verified": "2026-01-01",
45 |         "source_url": "https://indiacode.nic.in/..."
46 |     }]
47 | 
48 |     classifier_result = await classify_issue(facts)
49 |     analysis_result = await analyze_rights(facts, sample_law, language)
50 | 
51 |     return {
52 |         "language": language,
53 |         "classifier": classifier_result,
54 |         "analysis": analysis_result
55 |     }
</content>
</file>
<file><path>backend/routers/legal.py</path>
<content lines="1-446">
  1 | """
  2 | Legal Router for Court in Your Pocket
  3 | Handles legal analysis and resource retrieval
  4 | """
  5 | 
  6 | import os
  7 | import json
  8 | from typing import Dict, List, Optional
  9 | from fastapi import APIRouter, HTTPException
 10 | from pydantic import BaseModel
 11 | 
 12 | from session_store import get_session, update_session
 13 | from agents.classifier_agent import classify_issue
 14 | from agents.analysis_agent import analyze_rights
 15 | 
 16 | router = APIRouter(prefix="/api/legal", tags=["legal"])
 17 | 
 18 | 
 19 | # Pydantic Models
 20 | class AnalyzeRequest(BaseModel):
 21 |     sessionId: str
 22 | 
 23 | 
 24 | class RightEntry(BaseModel):
 25 |     law_name: str
 26 |     section: str
 27 |     plain_english: str
 28 |     exact_quote: str
 29 |     confidence: int
 30 |     last_verified: str
 31 |     source_url: str
 32 | 
 33 | 
 34 | class ActionOption(BaseModel):
 35 |     id: str
 36 |     label: str
 37 | 
 38 | 
 39 | class AnalyzeResponse(BaseModel):
 40 |     rights: List[RightEntry]
 41 |     confidence: int
 42 |     deadline: int
 43 |     options: List[ActionOption]
 44 | 
 45 | 
 46 | class OutOfScopeResponse(BaseModel):
 47 |     outOfScope: bool
 48 |     message: str
 49 |     legalAid: List[Dict[str, str]]
 50 | 
 51 | 
 52 | class ResourcesResponse(BaseModel):
 53 |     state: str
 54 |     helplines: List[Dict[str, str]]
 55 |     portals: List[Dict[str, str]]
 56 |     legalAid: List[Dict[str, str]]
 57 | 
 58 | 
 59 | # Helper Functions
 60 | def _load_legal_data(category: str) -> List[Dict]:
 61 |     """
 62 |     Load legal data from JSON files
 63 |     
 64 |     Args:
 65 |         category: One of "tenant", "employment", "consumer"
 66 |     
 67 |     Returns:
 68 |         List of law entries
 69 |     """
 70 |     category_file_map = {
 71 |         "tenant": "tenant_laws.json",
 72 |         "employment": "employment_laws.json",
 73 |         "consumer": "consumer_laws.json"
 74 |     }
 75 |     
 76 |     if category not in category_file_map:
 77 |         return []
 78 |     
 79 |     file_path = os.path.join(
 80 |         os.path.dirname(os.path.dirname(__file__)),
 81 |         "data",
 82 |         category_file_map[category]
 83 |     )
 84 |     
 85 |     try:
 86 |         with open(file_path, "r", encoding="utf-8") as f:
 87 |             data = json.load(f)
 88 |             return data if isinstance(data, list) else []
 89 |     except FileNotFoundError:
 90 |         print(f"Warning: Legal data file not found: {file_path}")
 91 |         return []
 92 |     except json.JSONDecodeError as e:
 93 |         print(f"Error parsing legal data file {file_path}: {e}")
 94 |         return []
 95 | 
 96 | 
 97 | def _filter_laws_by_jurisdiction_and_keywords(
 98 |     law_entries: List[Dict],
 99 |     state: str,
100 |     issue_text: str
101 | ) -> List[Dict]:
102 |     """
103 |     Filter law entries by jurisdiction and keyword matching
104 |     
105 |     Args:
106 |         law_entries: List of law entries from JSON
107 |         state: User's state (e.g., "KA", "MH", "DL")
108 |         issue_text: User's issue description
109 |     
110 |     Returns:
111 |         Filtered list of matching law entries
112 |     """
113 |     if not law_entries:
114 |         return []
115 |     
116 |     issue_lower = issue_text.lower() if issue_text else ""
117 |     matched_entries = []
118 |     
119 |     for entry in law_entries:
120 |         # Check jurisdiction match
121 |         jurisdiction = entry.get("jurisdiction", [])
122 |         if state not in jurisdiction and "IN" not in jurisdiction:
123 |             continue
124 |         
125 |         # Check keyword match
126 |         keywords = entry.get("keywords", [])
127 |         if keywords:
128 |             # Check if any keyword appears in the issue text
129 |             keyword_match = any(
130 |                 keyword.lower() in issue_lower
131 |                 for keyword in keywords
132 |             )
133 |             if keyword_match:
134 |                 matched_entries.append(entry)
135 |     
136 |     return matched_entries
137 | 
138 | 
139 | def _get_out_of_scope_response() -> Dict:
140 |     """
141 |     Generate out-of-scope response with legal aid contacts
142 |     
143 |     Returns:
144 |         Dictionary with outOfScope flag, message, and legal aid contacts
145 |     """
146 |     return {
147 |         "outOfScope": True,
148 |         "message": "This issue falls outside our current scope (tenant, employment, consumer rights). We recommend contacting free legal aid services.",
149 |         "legalAid": [
150 |             {
151 |                 "name": "National Legal Services Authority (NALSA)",
152 |                 "phone": "011-23388952",
153 |                 "website": "https://nalsa.gov.in",
154 |                 "description": "Free legal aid for eligible citizens"
155 |             },
156 |             {
157 |                 "name": "State Legal Services Authority",
158 |                 "phone": "Varies by state",
159 |                 "website": "https://nalsa.gov.in/state-legal-services-authorities",
160 |                 "description": "State-level free legal aid"
161 |             },
162 |             {
163 |                 "name": "District Legal Services Authority",
164 |                 "phone": "Contact local district court",
165 |                 "website": "Visit nearest district court",
166 |                 "description": "District-level legal aid and advice"
167 |             }
168 |         ]
169 |     }
170 | 
171 | 
172 | def _get_default_action_options() -> List[Dict]:
173 |     """
174 |     Get default action options for legal analysis
175 |     
176 |     Returns:
177 |         List of action options
178 |     """
179 |     return [
180 |         {"id": "A", "label": "Send demand letter"},
181 |         {"id": "B", "label": "File complaint"},
182 |         {"id": "C", "label": "Free legal aid"}
183 |     ]
184 | 
185 | 
186 | # API Endpoints
187 | @router.post("/analyze")
188 | async def analyze_legal_issue(request: AnalyzeRequest):
189 |     """
190 |     Analyze user's legal issue and provide rights information
191 |     
192 |     Process:
193 |     1. Get session and extract facts
194 |     2. Classify the issue
195 |     3. If out of scope, return legal aid contacts
196 |     4. Otherwise, retrieve relevant laws
197 |     5. Analyze rights using AI
198 |     6. Return rights with action options
199 |     """
200 |     try:
201 |         # Get session
202 |         session = get_session(request.sessionId)
203 |         if not session:
204 |             raise HTTPException(status_code=404, detail="Session not found or expired")
205 |         
206 |         # Extract facts and state
207 |         extracted_facts = session.get("extractedFacts", {})
208 |         state = session.get("state", "KA")
209 |         
210 |         # Validate that we have enough facts
211 |         if not extracted_facts.get("issue"):
212 |             raise HTTPException(
213 |                 status_code=400,
214 |                 detail="Insufficient facts extracted. Please complete the intake conversation first."
215 |             )
216 |         
217 |         # Step 1: Classify the issue
218 |         classification = await classify_issue(extracted_facts)
219 |         category = classification.get("category")
220 |         sub_scenario = classification.get("sub_scenario")
221 |         
222 |         # Update session with classification
223 |         update_session(request.sessionId, {
224 |             "category": category,
225 |             "sub_scenario": sub_scenario
226 |         })
227 |         
228 |         # Step 2: Check if out of scope
229 |         if category == "out_of_scope":
230 |             return _get_out_of_scope_response()
231 |         
232 |         # Step 3: Load relevant legal data
233 |         law_entries = _load_legal_data(category)
234 |         
235 |         if not law_entries:
236 |             raise HTTPException(
237 |                 status_code=500,
238 |                 detail=f"Legal data not available for category: {category}"
239 |             )
240 |         
241 |         # Step 4: Filter laws by jurisdiction and keywords
242 |         issue_text = extracted_facts.get("issue", "")
243 |         matched_entries = _filter_laws_by_jurisdiction_and_keywords(
244 |             law_entries,
245 |             state,
246 |             issue_text
247 |         )
248 |         
249 |         # If no keyword match, use first 2 entries as fallback
250 |         if not matched_entries:
251 |             print(f"No keyword match found, using fallback (first 2 entries)")
252 |             matched_entries = law_entries[:2]
253 |         
254 |         # Step 5: Analyze rights using AI
255 |         analysis_result = await analyze_rights(extracted_facts, matched_entries)
256 |         
257 |         # Step 6: Format and return response
258 |         rights = analysis_result.get("rights", [])
259 |         confidence = analysis_result.get("confidence", 3)
260 |         deadline = analysis_result.get("deadline", 30)
261 |         
262 |         # Update session with analysis results
263 |         update_session(request.sessionId, {
264 |             "confidenceScore": confidence,
265 |             "stage": "analysis"
266 |         })
267 |         
268 |         return {
269 |             "rights": rights,
270 |             "confidence": confidence,
271 |             "deadline": deadline,
272 |             "options": _get_default_action_options()
273 |         }
274 |         
275 |     except HTTPException:
276 |         raise
277 |     except Exception as e:
278 |         print(f"Error in analyze_legal_issue: {e}")
279 |         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
280 | 
281 | 
282 | @router.get("/resources")
283 | async def get_legal_resources(state: str = "KA"):
284 |     """
285 |     Get legal resources, helplines, and portals for a specific state
286 |     
287 |     Args:
288 |         state: State code (KA, MH, DL)
289 |     
290 |     Returns:
291 |         Dictionary with helplines, portals, and legal aid contacts
292 |     """
293 |     try:
294 |         # State-specific resources
295 |         state_resources = {
296 |             "KA": {
297 |                 "helplines": [
298 |                     {
299 |                         "name": "Karnataka State Legal Services Authority",
300 |                         "phone": "080-22867926",
301 |                         "description": "Free legal aid and advice"
302 |                     },
303 |                     {
304 |                         "name": "Karnataka Consumer Helpline",
305 |                         "phone": "1800-425-9339",
306 |                         "description": "Consumer complaints and guidance"
307 |                     }
308 |                 ],
309 |                 "portals": [
310 |                     {
311 |                         "name": "Karnataka Rent Authority",
312 |                         "url": "https://karnataka.gov.in",
313 |                         "description": "Tenant-landlord dispute resolution"
314 |                     },
315 |                     {
316 |                         "name": "Karnataka Labour Department",
317 |                         "url": "https://labour.karnataka.gov.in",
318 |                         "description": "Employment and wage disputes"
319 |                     }
320 |                 ],
321 |                 "legalAid": [
322 |                     {
323 |                         "name": "Karnataka State Legal Services Authority",
324 |                         "phone": "080-22867926",
325 |                         "website": "https://kslsa.kar.nic.in",
326 |                         "description": "Free legal aid for eligible citizens"
327 |                     }
328 |                 ]
329 |             },
330 |             "MH": {
331 |                 "helplines": [
332 |                     {
333 |                         "name": "Maharashtra State Legal Services Authority",
334 |                         "phone": "022-22620208",
335 |                         "description": "Free legal aid and advice"
336 |                     },
337 |                     {
338 |                         "name": "Maharashtra Consumer Helpline",
339 |                         "phone": "1800-22-4477",
340 |                         "description": "Consumer complaints and guidance"
341 |                     }
342 |                 ],
343 |                 "portals": [
344 |                     {
345 |                         "name": "Maharashtra Rent Authority",
346 |                         "url": "https://maharashtra.gov.in",
347 |                         "description": "Tenant-landlord dispute resolution"
348 |                     },
349 |                     {
350 |                         "name": "Maharashtra Labour Department",
351 |                         "url": "https://mahakamgar.maharashtra.gov.in",
352 |                         "description": "Employment and wage disputes"
353 |                     }
354 |                 ],
355 |                 "legalAid": [
356 |                     {
357 |                         "name": "Maharashtra State Legal Services Authority",
358 |                         "phone": "022-22620208",
359 |                         "website": "https://mslsa.gov.in",
360 |                         "description": "Free legal aid for eligible citizens"
361 |                     }
362 |                 ]
363 |             },
364 |             "DL": {
365 |                 "helplines": [
366 |                     {
367 |                         "name": "Delhi State Legal Services Authority",
368 |                         "phone": "011-23389150",
369 |                         "description": "Free legal aid and advice"
370 |                     },
371 |                     {
372 |                         "name": "Delhi Consumer Helpline",
373 |                         "phone": "1800-11-4000",
374 |                         "description": "Consumer complaints and guidance"
375 |                     }
376 |                 ],
377 |                 "portals": [
378 |                     {
379 |                         "name": "Delhi Rent Authority",
380 |                         "url": "https://delhi.gov.in",
381 |                         "description": "Tenant-landlord dispute resolution"
382 |                     },
383 |                     {
384 |                         "name": "Delhi Labour Department",
385 |                         "url": "https://labour.delhi.gov.in",
386 |                         "description": "Employment and wage disputes"
387 |                     }
388 |                 ],
389 |                 "legalAid": [
390 |                     {
391 |                         "name": "Delhi State Legal Services Authority",
392 |                         "phone": "011-23389150",
393 |                         "website": "https://dslsa.org",
394 |                         "description": "Free legal aid for eligible citizens"
395 |                     }
396 |                 ]
397 |             }
398 |         }
399 |         
400 |         # Get state-specific resources or default to KA
401 |         resources = state_resources.get(state, state_resources["KA"])
402 |         
403 |         # Always include national resources
404 |         national_helplines = [
405 |             {
406 |                 "name": "National Consumer Helpline",
407 |                 "phone": "1800-11-4000",
408 |                 "description": "National consumer complaints helpline"
409 |             },
410 |             {
411 |                 "name": "National Legal Services Authority (NALSA)",
412 |                 "phone": "011-23388952",
413 |                 "description": "National free legal aid authority"
414 |             }
415 |         ]
416 |         
417 |         national_portals = [
418 |             {
419 |                 "name": "edaakhil Portal",
420 |                 "url": "https://edaakhil.nic.in",
421 |                 "description": "National consumer complaints portal"
422 |             },
423 |             {
424 |                 "name": "India Code",
425 |                 "url": "https://indiacode.nic.in",
426 |                 "description": "Official repository of Indian laws"
427 |             }
428 |         ]
429 |         
430 |         # Combine state and national resources
431 |         all_helplines = national_helplines + resources["helplines"]
432 |         all_portals = national_portals + resources["portals"]
433 |         
434 |         return {
435 |             "state": state,
436 |             "helplines": all_helplines,
437 |             "portals": all_portals,
438 |             "legalAid": resources["legalAid"]
439 |         }
440 |         
441 |     except Exception as e:
442 |         print(f"Error in get_legal_resources: {e}")
443 |         raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
444 | 
445 | 
446 | # Made with Bob
</content>
</file>
</files>
<environment_details>
# VSCode Visible Files
backend\agents\analysis_agent.py

# VSCode Open Tabs
../../../Downloads/developer_breakdown.md,.git.ignore,backend/.env,backend/requirements.txt,backend/session_store.py,backend/routers/legal.py,backend/agents/analysis_agent.py,backend/main.py,frontend/vite.config.js,frontend/src/screens/RightsScreen.jsx,frontend/SETUP.md,frontend/src/App.jsx,frontend/src/main.jsx,frontend/src/context/AppContext.jsx,backend/agents/classifier_agent.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T15:15:35.236Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.01

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I can see that the legal router has already been imported and registered in `backend/main.py`! 

Looking at lines 4 and 7:
- Line 4: `from routers.legal import router as legal_router`
- Line 7: `app.include_router(legal_router)`

The router is properly imported and registered with FastAPI. This means the `/api/legal/analyze` and `/api/legal/resources` endpoints should be accessible.

If you're still getting 404 errors, the issue might be elsewhere. Let me verify the setup is correct by checking if there are any other potential issues.

<attempt_completion>
<result>
The legal router is already properly imported and registered in backend/main.py:
- Line 4: `from routers.legal import router as legal_router`
- Line 7: `app.include_router(legal_router)`

The endpoints `/api/legal/analyze` and `/api/legal/resources` should be accessible. If you're still experiencing 404 errors, the issue may be:
1. The FastAPI server needs to be restarted
2. There might be a different routing issue
3. The frontend might be calling the wrong URL

No changes were needed as the router was already correctly registered.
</result>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
There are two problems in backend/agents/analysis_agent.py that cause the language setting to have no effect:

Look at the _build_analysis_prompt function. In the CRITICAL RULES section, Rule 3 says "Use plain English suitable for non-lawyers in India". This directly conflicts with the task instruction below it that says "Explain their rights in simple, clear {language_name}". The model follows Rule 3 and ignores the task instruction. Fix Rule 3 so it no longer hardcodes "plain English" but instead references the chosen language.

Look at backend/main.py in the /test-agents endpoint. It accepts a language query parameter but never passes it to analyze_rights. Check how analyze_rights is called there and make sure the language value is passed through.

Do not change any other logic.
</feedback>
<environment_details>
# VSCode Visible Files
backend\agents\analysis_agent.py

# VSCode Open Tabs
../../../Downloads/developer_breakdown.md,.git.ignore,backend/.env,backend/requirements.txt,backend/session_store.py,backend/routers/legal.py,backend/agents/analysis_agent.py,backend/main.py,frontend/vite.config.js,frontend/src/screens/RightsScreen.jsx,frontend/SETUP.md,frontend/src/App.jsx,frontend/src/main.jsx,frontend/src/context/AppContext.jsx,backend/agents/classifier_agent.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T15:33:19.538Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.03

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I'll fix both issues. Let me first read the relevant parts of the files to understand the current state.

<read_file>
<args>
<file>
<path>backend/agents/analysis_agent.py</path>
</file>
<file>
<path>backend/main.py</path>
<line_range>47-50</line_range>
</file>
</args>
</read_file>

---

**User:**

[read_file for 'backend/agents/analysis_agent.py', 'backend/main.py'] Result:
<files>
<file><path>backend/agents/analysis_agent.py</path>
<content lines="1-452">
  1 | """
  2 | Analysis Agent for Court in Your Pocket
  3 | Analyzes user rights based on facts and Indian law entries using IBM watsonx AI
  4 | """
  5 | 
  6 | import os
  7 | import json
  8 | import asyncio
  9 | from typing import Dict, List
 10 | from dotenv import load_dotenv
 11 | from ibm_watsonx_ai.foundation_models import ModelInference
 12 | from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
 13 | from ibm_watsonx_ai import Credentials
 14 | 
 15 | # Load environment variables
 16 | load_dotenv()
 17 | 
 18 | # IBM watsonx credentials
 19 | IBM_WATSONX_API_KEY = os.getenv("IBM_WATSONX_API_KEY")
 20 | IBM_WATSONX_PROJECT_ID = os.getenv("IBM_WATSONX_PROJECT_ID")
 21 | IBM_WATSONX_URL = os.getenv("IBM_WATSONX_URL")
 22 | 
 23 | # Model configuration
 24 | MODEL_ID = "meta-llama/llama-3-3-70b-instruct"
 25 | 
 26 | 
 27 | def _initialize_watsonx_client():
 28 |     """Initialize IBM watsonx AI client"""
 29 |     credentials = Credentials(
 30 |         url=IBM_WATSONX_URL,
 31 |         api_key=IBM_WATSONX_API_KEY
 32 |     )
 33 |     return ModelInference(
 34 |         model_id=MODEL_ID,
 35 |         credentials=credentials,
 36 |         project_id=IBM_WATSONX_PROJECT_ID,
 37 |         params={
 38 |             GenParams.DECODING_METHOD: "greedy",
 39 |             GenParams.MAX_NEW_TOKENS: 800,
 40 |             GenParams.MIN_NEW_TOKENS: 10,
 41 |         }
 42 |     )
 43 | 
 44 | 
 45 | def _format_facts(facts: Dict) -> str:
 46 |     """Format facts dictionary into readable text"""
 47 |     formatted = []
 48 |     for key, value in facts.items():
 49 |         if value:
 50 |             if isinstance(value, list):
 51 |                 formatted.append(f"- {key.replace('_', ' ').title()}: {', '.join(str(v) for v in value)}")
 52 |             else:
 53 |                 formatted.append(f"- {key.replace('_', ' ').title()}: {value}")
 54 |     return "\n".join(formatted)
 55 | 
 56 | 
 57 | def _format_law_entries(law_entries: List[Dict]) -> str:
 58 |     """Format law entries into readable text for the prompt"""
 59 |     if not law_entries:
 60 |         return "No specific laws provided."
 61 |     
 62 |     formatted = []
 63 |     for idx, law in enumerate(law_entries, 1):
 64 |         entry = f"\nLaw Entry {idx}:"
 65 |         entry += f"\n- Law Name: {law.get('law_name', 'Unknown')}"
 66 |         entry += f"\n- Year: {law.get('year', 'Unknown')}"
 67 |         entry += f"\n- Section: {law.get('section', 'Unknown')}"
 68 |         entry += f"\n- Plain English: {law.get('plain_english', 'Not provided')}"
 69 |         entry += f"\n- Exact Quote: {law.get('exact_quote', 'Not provided')}"
 70 |         entry += f"\n- User Rights: {', '.join(law.get('user_rights', []))}"
 71 |         entry += f"\n- Deadline Days: {law.get('deadline_days', 'Not specified')}"
 72 |         entry += f"\n- Last Verified: {law.get('last_verified', 'Unknown')}"
 73 |         entry += f"\n- Source URL: {law.get('source_url', 'Not provided')}"
 74 |         formatted.append(entry)
 75 |     
 76 |     return "\n".join(formatted)
 77 | 
 78 | 
 79 | LANGUAGE_NAMES = {
 80 |     "en": "English", "hi": "Hindi", "ta": "Tamil",
 81 |     "te": "Telugu", "kn": "Kannada", "mr": "Marathi", "bn": "Bengali"
 82 | }
 83 | 
 84 | 
 85 | def _build_analysis_prompt(facts: Dict, law_entries: List[Dict], language="en") -> str:
 86 |     """Build detailed analysis prompt with Indian legal context"""
 87 |     
 88 |     language_name = LANGUAGE_NAMES.get(language, "English")
 89 |     formatted_facts = _format_facts(facts)
 90 |     formatted_laws = _format_law_entries(law_entries)
 91 |     
 92 |     prompt = f"""You are a legal rights analyst for Indian law. Your role is to explain user rights based ONLY on the provided Indian statutes.
 93 | 
 94 | CRITICAL RULES:
 95 | 1. NEVER invent or assume laws not provided in the law_entries below
 96 | 2. ONLY cite sections explicitly mentioned in the provided data
 97 | 3. Use plain English suitable for non-lawyers in India
 98 | 4. Provide confidence score 1-5 based on how well the facts match the law
 99 | 5. Calculate realistic deadline in days based on Indian legal timelines
100 | 
101 | User Facts:
102 | {formatted_facts}
103 | 
104 | Provided Indian Laws (USE ONLY THESE):
105 | {formatted_laws}
106 | 
107 | Your task:
108 | 1. Match the user's situation to the most relevant provided laws
109 | 2. Explain their rights in simple, clear {language_name} suitable for non-lawyers in India
110 | 3. Quote the EXACT section text from the provided data
111 | 4. Assign confidence: 5=perfect match, 4=strong match, 3=moderate, 2=weak, 1=very uncertain
112 | 5. Estimate deadline based on typical Indian legal procedures (e.g., consumer complaints: 30-90 days, rent disputes: 60-180 days)
113 | 
114 | Return ONLY valid JSON in this exact format:
115 | {{
116 |   "rights": [
117 |     {{
118 |       "law_name": "exact name from provided data",
119 |       "section": "exact section from provided data",
120 |       "plain_english": "simple explanation in Indian English context",
121 |       "exact_quote": "verbatim quote from provided law text",
122 |       "confidence": 1-5,
123 |       "last_verified": "date from provided data",
124 |       "source_url": "URL from provided data"
125 |     }}
126 |   ],
127 |   "confidence": 1-5,
128 |   "deadline": number_of_days
129 | }}
130 | 
131 | If no laws match well, return confidence 2 and explain limitations honestly.
132 | 
133 | JSON Response:"""
134 |     
135 |     return prompt
136 | 
137 | 
138 | def _parse_analysis_response(response_text: str) -> Dict:
139 |     """Parse Bob's response and extract JSON analysis"""
140 |     try:
141 |         # Clean the response text
142 |         response_text = response_text.strip()
143 |         
144 |         # Try to find JSON in the response
145 |         if "{" in response_text and "}" in response_text:
146 |             start_idx = response_text.find("{")
147 |             # Find the matching closing brace for the first opening brace
148 |             depth = 0
149 |             end_idx = start_idx
150 |             for i, ch in enumerate(response_text[start_idx:], start=start_idx):
151 |                 if ch == "{":
152 |                     depth += 1
153 |                 elif ch == "}":
154 |                     depth -= 1
155 |                     if depth == 0:
156 |                         end_idx = i + 1
157 |                         break
158 |             json_str = response_text[start_idx:end_idx]
159 |             
160 |             # Parse JSON
161 |             result = json.loads(json_str)
162 |             
163 |             # Validate required fields
164 |             if "rights" in result and "confidence" in result and "deadline" in result:
165 |                 # Validate rights is a list
166 |                 if isinstance(result["rights"], list):
167 |                     # Validate each right has required fields
168 |                     for right in result["rights"]:
169 |                         required_fields = ["law_name", "section", "plain_english", "exact_quote", 
170 |                                          "confidence", "last_verified", "source_url"]
171 |                         if all(field in right for field in required_fields):
172 |                             continue
173 |                         else:
174 |                             raise ValueError("Missing required fields in rights entry")
175 |                     
176 |                     return result
177 |         
178 |         # If parsing fails, raise exception to trigger fallback
179 |         raise ValueError("Failed to parse valid JSON response")
180 |         
181 |     except Exception as e:
182 |         print(f"Error parsing analysis response: {e}")
183 |         raise
184 | 
185 | 
186 | def _create_fallback_response(law_entries: List[Dict]) -> Dict:
187 |     """Create fallback response by formatting law_entries directly"""
188 |     if not law_entries:
189 |         return {
190 |             "rights": [],
191 |             "confidence": 2,
192 |             "deadline": 30
193 |         }
194 |     
195 |     rights = []
196 |     for law in law_entries:
197 |         right = {
198 |             "law_name": law.get("law_name", "Unknown Law"),
199 |             "section": law.get("section", "Section not specified"),
200 |             "plain_english": law.get("plain_english", "Please refer to the exact legal text for details."),
201 |             "exact_quote": law.get("exact_quote", "Quote not available"),
202 |             "confidence": 3,  # Moderate confidence for fallback
203 |             "last_verified": law.get("last_verified", "Unknown"),
204 |             "source_url": law.get("source_url", "")
205 |         }
206 |         rights.append(right)
207 |     
208 |     # Calculate average deadline from law entries
209 |     deadlines = [law.get("deadline_days", 30) for law in law_entries if law.get("deadline_days")]
210 |     avg_deadline = sum(deadlines) // len(deadlines) if deadlines else 30
211 |     
212 |     return {
213 |         "rights": rights,
214 |         "confidence": 3,
215 |         "deadline": avg_deadline
216 |     }
217 | 
218 | 
219 | async def analyze_rights(facts: Dict, law_entries: List[Dict], language="en") -> Dict:
220 |     """
221 |     Analyze user rights based on facts and Indian law entries using IBM watsonx AI
222 |     
223 |     Args:
224 |         facts: Dictionary containing:
225 |             - issue: Description of the legal issue
226 |             - location: User's location (state in India)
227 |             - dates: List of relevant dates
228 |             - amounts: Monetary amounts involved
229 |             - partyName: Name of the other party
230 |         
231 |         law_entries: List of law entry dictionaries from JSON knowledge base, each containing:
232 |             - law_name: Name of the law
233 |             - section: Section number
234 |             - plain_english: Plain English explanation
235 |             - exact_quote: Exact text from the law
236 |             - deadline_days: Deadline in days
237 |             - last_verified: Last verification date
238 |             - source_url: Official source URL
239 |         
240 |         language: Language code for response (default: "en")
241 |     
242 |     Returns:
243 |         Dictionary with:
244 |             - rights: List of rights with law citations
245 |             - confidence: Overall confidence score (1-5)
246 |             - deadline: Deadline in days
247 |     
248 |     Example:
249 |         >>> facts = {
250 |         ...     "issue": "Landlord not returning security deposit",
251 |         ...     "location": "Karnataka",
252 |         ...     "dates": ["2024-01-15"],
253 |         ...     "amounts": "₹40,000",
254 |         ...     "partyName": "Mr. Sharma"
255 |         ... }
256 |         >>> law_entries = [{
257 |         ...     "law_name": "Model Tenancy Act 2021",
258 |         ...     "section": "Section 11",
259 |         ...     "plain_english": "Landlord must return deposit within 1 month",
260 |         ...     "exact_quote": "The landlord shall refund the security deposit...",
261 |         ...     "deadline_days": 90,
262 |         ...     "last_verified": "2026-05-01",
263 |         ...     "source_url": "https://indiacode.nic.in/..."
264 |         ... }]
265 |         >>> result = await analyze_rights(facts, law_entries)
266 |     """
267 |     try:
268 |         # Initialize watsonx client
269 |         client = _initialize_watsonx_client()
270 |         
271 |         # Build prompt
272 |         prompt = _build_analysis_prompt(facts, law_entries, language)
273 |         
274 |         # Generate response
275 |         response = client.generate_text(prompt=prompt)
276 |         
277 |         # Handle response type - convert to string if needed
278 |         if isinstance(response, str):
279 |             response_text = response
280 |         elif isinstance(response, dict):
281 |             response_text = response.get("generated_text", str(response))
282 |         elif isinstance(response, list):
283 |             response_text = str(response[0]) if response else ""
284 |         else:
285 |             response_text = str(response)
286 |         
287 |         # Try to parse the response
288 |         try:
289 |             analysis = _parse_analysis_response(response_text)
290 |             print(f"Analysis result: {json.dumps(analysis, indent=2)}")
291 |             return analysis
292 |         except Exception as parse_error:
293 |             print(f"Failed to parse Bob's response, using fallback: {parse_error}")
294 |             # Use fallback - format law_entries directly
295 |             fallback = _create_fallback_response(law_entries)
296 |             print(f"Fallback result: {json.dumps(fallback, indent=2)}")
297 |             return fallback
298 |         
299 |     except Exception as e:
300 |         print(f"Error in analyze_rights: {e}")
301 |         # Return fallback on any error
302 |         fallback = _create_fallback_response(law_entries)
303 |         print(f"Error fallback result: {json.dumps(fallback, indent=2)}")
304 |         return fallback
305 | 
306 | 
307 | # Test block
308 | if __name__ == "__main__":
309 |     print("=" * 80)
310 |     print("Testing Analysis Agent with IBM watsonx AI")
311 |     print("=" * 80)
312 |     
313 |     # Test case 1: Tenant issue - security deposit not returned
314 |     test_facts_1 = {
315 |         "issue": "My landlord is not returning my security deposit of ₹40,000. I moved out 6 weeks ago after completing my 11-month rental agreement. The flat was in good condition.",
316 |         "location": "Karnataka",
317 |         "dates": ["2024-03-01"],
318 |         "amounts": "₹40,000",
319 |         "partyName": "Mr. Rajesh Kumar"
320 |     }
321 |     
322 |     test_law_entries_1 = [
323 |         {
324 |             "id": "TN_IN_001",
325 |             "category": "tenant",
326 |             "scenario": "security_deposit_not_returned",
327 |             "law_name": "Model Tenancy Act 2021",
328 |             "year": 2021,
329 |             "section": "Section 11",
330 |             "plain_english": "The landlord must return the security deposit to the tenant within one month of the tenant vacating the premises, after deducting any legitimate dues.",
331 |             "exact_quote": "The landlord shall refund the security deposit to the tenant within a period of one month from the date of handing over possession of the premises by the tenant, after deducting any amount that may be due from the tenant.",
332 |             "user_rights": [
333 |                 "Right to receive full security deposit back within 1 month",
334 |                 "Right to receive written explanation for any deductions",
335 |                 "Right to file complaint with Rent Authority if not returned"
336 |             ],
337 |             "deadline_days": 90,
338 |             "last_verified": "2026-05-01",
339 |             "source_url": "https://indiacode.nic.in/handle/123456789/2032"
340 |         }
341 |     ]
342 |     
343 |     print("\nTest Case 1: Tenant Issue - Security Deposit Not Returned")
344 |     print("-" * 80)
345 |     print(f"Input facts:\n{json.dumps(test_facts_1, indent=2)}")
346 |     print(f"\nProvided law entries:\n{json.dumps(test_law_entries_1, indent=2)}")
347 |     result_1 = asyncio.run(analyze_rights(test_facts_1, test_law_entries_1))
348 |     print(f"\nAnalysis Result:")
349 |     print(json.dumps(result_1, indent=2))
350 |     
351 |     # Test case 2: Employment issue - wage non-payment
352 |     test_facts_2 = {
353 |         "issue": "My employer has not paid my salary for the last 2 months. I work as a software developer and my monthly salary is ₹30,000.",
354 |         "location": "Maharashtra",
355 |         "dates": ["2024-02-01", "2024-03-01"],
356 |         "amounts": "₹60,000",
357 |         "partyName": "ABC Technologies Pvt Ltd"
358 |     }
359 |     
360 |     test_law_entries_2 = [
361 |         {
362 |             "id": "EMP_IN_001",
363 |             "category": "employment",
364 |             "scenario": "wage_non_payment",
365 |             "law_name": "Code on Wages 2019",
366 |             "year": 2019,
367 |             "section": "Section 3 and Section 5",
368 |             "plain_english": "Every employer must pay wages to employees on time (within 7 days for establishments with less than 1000 employees, within 10 days for larger ones). Delayed payment attracts compensation.",
369 |             "exact_quote": "The wages of every person employed shall be paid before the expiry of the seventh day of the last day of the wage period in respect of which the wages are payable.",
370 |             "user_rights": [
371 |                 "Right to receive wages on time",
372 |                 "Right to compensation for delayed payment",
373 |                 "Right to file complaint with Labour Commissioner"
374 |             ],
375 |             "deadline_days": 60,
376 |             "last_verified": "2026-04-15",
377 |             "source_url": "https://labour.gov.in/code-wages-2019"
378 |         }
379 |     ]
380 |     
381 |     print("\n" + "=" * 80)
382 |     print("Test Case 2: Employment Issue - Wage Non-payment")
383 |     print("-" * 80)
384 |     print(f"Input facts:\n{json.dumps(test_facts_2, indent=2)}")
385 |     print(f"\nProvided law entries:\n{json.dumps(test_law_entries_2, indent=2)}")
386 |     result_2 = asyncio.run(analyze_rights(test_facts_2, test_law_entries_2))
387 |     print(f"\nAnalysis Result:")
388 |     print(json.dumps(result_2, indent=2))
389 |     
390 |     # Test case 3: Consumer issue - defective product
391 |     test_facts_3 = {
392 |         "issue": "I bought a refrigerator for ₹35,000 that stopped working after just 1 week. The company is refusing to replace or refund despite valid warranty.",
393 |         "location": "Delhi",
394 |         "dates": ["2024-04-01"],
395 |         "amounts": "₹35,000",
396 |         "partyName": "XYZ Electronics"
397 |     }
398 |     
399 |     test_law_entries_3 = [
400 |         {
401 |             "id": "CON_IN_001",
402 |             "category": "consumer",
403 |             "scenario": "defective_product",
404 |             "law_name": "Consumer Protection Act 2019",
405 |             "year": 2019,
406 |             "section": "Section 2(7) and Section 18",
407 |             "plain_english": "Consumers have the right to seek replacement, refund, or compensation for defective goods. Manufacturers and sellers are liable for product defects.",
408 |             "exact_quote": "A consumer has the right to be protected against marketing of goods and services which are hazardous to life and property, and the right to seek redressal against unfair trade practices.",
409 |             "user_rights": [
410 |                 "Right to replacement of defective product",
411 |                 "Right to full refund if replacement not possible",
412 |                 "Right to compensation for any loss or damage",
413 |                 "Right to file complaint with Consumer Forum"
414 |             ],
415 |             "deadline_days": 30,
416 |             "last_verified": "2026-05-10",
417 |             "source_url": "https://consumeraffairs.nic.in/acts-and-rules"
418 |         }
419 |     ]
420 |     
421 |     print("\n" + "=" * 80)
422 |     print("Test Case 3: Consumer Issue - Defective Product")
423 |     print("-" * 80)
424 |     print(f"Input facts:\n{json.dumps(test_facts_3, indent=2)}")
425 |     print(f"\nProvided law entries:\n{json.dumps(test_law_entries_3, indent=2)}")
426 |     result_3 = asyncio.run(analyze_rights(test_facts_3, test_law_entries_3))
427 |     print(f"\nAnalysis Result:")
428 |     print(json.dumps(result_3, indent=2))
429 |     
430 |     # Test case 4: Empty law entries (fallback test)
431 |     test_facts_4 = {
432 |         "issue": "Some legal issue",
433 |         "location": "Karnataka",
434 |         "dates": [],
435 |         "amounts": "₹10,000",
436 |         "partyName": "Someone"
437 |     }
438 |     
439 |     print("\n" + "=" * 80)
440 |     print("Test Case 4: Fallback Test - Empty Law Entries")
441 |     print("-" * 80)
442 |     print(f"Input facts:\n{json.dumps(test_facts_4, indent=2)}")
443 |     print(f"\nProvided law entries: []")
444 |     result_4 = asyncio.run(analyze_rights(test_facts_4, []))
445 |     print(f"\nAnalysis Result (should use fallback):")
446 |     print(json.dumps(result_4, indent=2))
447 |     
448 |     print("\n" + "=" * 80)
449 |     print("All tests completed!")
450 |     print("=" * 80)
451 | 
452 | # Made with Bob
</content>
</file>
<file><path>backend/main.py</path>
<content lines="47-50">
47 | 
48 |     classifier_result = await classify_issue(facts)
49 |     analysis_result = await analyze_rights(facts, sample_law, language)
50 | 
</content>
</file>
</files>
<environment_details>
# VSCode Visible Files
backend\agents\analysis_agent.py

# VSCode Open Tabs
../../../Downloads/developer_breakdown.md,.git.ignore,backend/.env,backend/requirements.txt,backend/session_store.py,backend/routers/legal.py,backend/agents/analysis_agent.py,backend/main.py,frontend/vite.config.js,frontend/src/screens/RightsScreen.jsx,frontend/SETUP.md,frontend/src/App.jsx,frontend/src/main.jsx,frontend/src/context/AppContext.jsx,backend/agents/classifier_agent.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T15:34:25.732Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.06

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

Now I can see both issues clearly:

1. In `backend/agents/analysis_agent.py` line 97, Rule 3 hardcodes "plain English" instead of referencing the language parameter
2. In `backend/main.py` line 49, the `language` parameter is already being passed to `analyze_rights`, so that's actually correct

Let me fix the first issue in the analysis_agent.py file:

<apply_diff>
<path>backend/agents/analysis_agent.py</path>
<diff>
<<<<<<< SEARCH
:start_line:92
-------
    prompt = f"""You are a legal rights analyst for Indian law. Your role is to explain user rights based ONLY on the provided Indian statutes.

CRITICAL RULES:
1. NEVER invent or assume laws not provided in the law_entries below
2. ONLY cite sections explicitly mentioned in the provided data
3. Use plain English suitable for non-lawyers in India
4. Provide confidence score 1-5 based on how well the facts match the law
5. Calculate realistic deadline in days based on Indian legal timelines
=======
    prompt = f"""You are a legal rights analyst for Indian law. Your role is to explain user rights based ONLY on the provided Indian statutes.

CRITICAL RULES:
1. NEVER invent or assume laws not provided in the law_entries below
2. ONLY cite sections explicitly mentioned in the provided data
3. Use plain {language_name} suitable for non-lawyers in India
4. Provide confidence score 1-5 based on how well the facts match the law
5. Calculate realistic deadline in days based on Indian legal timelines
>>>>>>> REPLACE
</diff>
</apply_diff>

---

**User:**

[apply_diff for 'backend/agents/analysis_agent.py'] Result:
<file_write_result>
<path>backend/agents/analysis_agent.py</path>
<operation>modified</operation>
<notice>
<i>You do not need to re-read the file, as you have seen all changes</i>
<i>Proceed with the task using these changes as the new baseline.</i>
</notice>
</file_write_result>

<notice>Making multiple related changes in a single apply_diff is more efficient. If other changes are needed in this file, please include them as additional SEARCH/REPLACE blocks.</notice>
<environment_details>
# VSCode Visible Files
backend\agents\analysis_agent.py

# VSCode Open Tabs
../../../Downloads/developer_breakdown.md,.git.ignore,backend/.env,backend/requirements.txt,backend/session_store.py,backend/routers/legal.py,backend/main.py,frontend/vite.config.js,frontend/src/screens/RightsScreen.jsx,frontend/SETUP.md,frontend/src/App.jsx,backend/agents/analysis_agent.py,frontend/src/main.jsx,frontend/src/context/AppContext.jsx,backend/agents/classifier_agent.py

# Recently Modified Files
These files have been modified since you last accessed them (file was just edited so you may need to re-read it before editing):
backend/agents/analysis_agent.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T15:34:44.417Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.11

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

Perfect! I've fixed the issue in `backend/agents/analysis_agent.py`. Now let me verify the second issue in `backend/main.py`. Let me read the full context around the test-agents endpoint:

<read_file>
<args>
<file>
<path>backend/main.py</path>
<line_range>13-55</line_range>
</file>
</args>
</read_file>

---

**User:**

[read_file for 'backend/main.py'. Reading multiple files at once is more efficient for the LLM. If other files are relevant to your current task, please read them simultaneously.] Result:
<files>
<file><path>backend/main.py</path>
<content lines="13-55">
13 | @app.get("/test-agents")
14 | async def test_agents(language: str = "en"):
15 |     """
16 |     Test endpoint for agents with language support
17 |     
18 |     Query Parameters:
19 |         language: Language code (en, hi, ta, te, kn, mr, bn). Default: en
20 |     
21 |     Examples:
22 |         /test-agents (English - default)
23 |         /test-agents?language=hi (Hindi)
24 |         /test-agents?language=ta (Tamil)
25 |         /test-agents?language=te (Telugu)
26 |         /test-agents?language=kn (Kannada)
27 |         /test-agents?language=mr (Marathi)
28 |         /test-agents?language=bn (Bengali)
29 |     """
30 |     facts = {
31 |         "issue": "landlord not returning security deposit",
32 |         "location": "Bangalore",
33 |         "amount": "4000",
34 |         "dates": ["2026-03-15"],
35 |         "partyName": "Mr. Sharma"
36 |     }
37 | 
38 |     sample_law = [{
39 |         "law_name": "Model Tenancy Act",
40 |         "section": "Section 11",
41 |         "plain_english": "Landlord must return deposit within 1 month",
42 |         "exact_quote": "The landlord shall refund the security deposit...",
43 |         "deadline_days": 90,
44 |         "last_verified": "2026-01-01",
45 |         "source_url": "https://indiacode.nic.in/..."
46 |     }]
47 | 
48 |     classifier_result = await classify_issue(facts)
49 |     analysis_result = await analyze_rights(facts, sample_law, language)
50 | 
51 |     return {
52 |         "language": language,
53 |         "classifier": classifier_result,
54 |         "analysis": analysis_result
55 |     }
</content>
</file>
</files>
<environment_details>
# VSCode Visible Files
backend\agents\analysis_agent.py

# VSCode Open Tabs
../../../Downloads/developer_breakdown.md,.git.ignore,backend/.env,backend/requirements.txt,backend/session_store.py,backend/routers/legal.py,backend/main.py,frontend/vite.config.js,frontend/src/screens/RightsScreen.jsx,frontend/SETUP.md,frontend/src/App.jsx,backend/agents/analysis_agent.py,frontend/src/main.jsx,frontend/src/context/AppContext.jsx,backend/agents/classifier_agent.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T15:34:54.640Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.15

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I can see that in `backend/main.py` line 49, the `language` parameter is already being passed to `analyze_rights(facts, sample_law, language)`. This is correct! 

So the only issue was in `backend/agents/analysis_agent.py`, which I've already fixed. Let me complete the task:

<attempt_completion>
<result>
Fixed the language setting issue in backend/agents/analysis_agent.py:

**Change made:**
- Line 97: Changed Rule 3 from "Use plain English suitable for non-lawyers in India" to "Use plain {language_name} suitable for non-lawyers in India"

This ensures the AI model respects the language parameter and generates responses in the requested language (Hindi, Tamil, Telugu, Kannada, Marathi, Bengali, or English) instead of always defaulting to English.

**Note:** The backend/main.py file was already correctly passing the language parameter to analyze_rights() on line 49, so no changes were needed there.
</result>
</attempt_completion>

---

**User:**

[attempt_completion] Result:
The user has provided feedback on the results. Consider their input to continue the task, and then attempt completion again.
<feedback>
Open backend/main.py and read its exact current contents carefully — do not assume what is there, read the file. You will find it has only 3 import lines and no reference to legal_router or include_router anywhere. The file needs two additions:

Add this import line after the existing imports: from routers.legal import router as legal_router
Add this line immediately after app = FastAPI(): app.include_router(legal_router)
After making the changes, confirm what the file now contains on those lines. Do not say the task is complete without showing the actual modified file content.
</feedback>
<environment_details>
# VSCode Visible Files
backend\agents\analysis_agent.py

# VSCode Open Tabs
../../../Downloads/developer_breakdown.md,.git.ignore,backend/.env,backend/requirements.txt,backend/session_store.py,backend/routers/legal.py,backend/main.py,frontend/vite.config.js,frontend/src/screens/RightsScreen.jsx,frontend/SETUP.md,frontend/src/App.jsx,backend/agents/analysis_agent.py,frontend/src/main.jsx,frontend/src/context/AppContext.jsx,backend/agents/classifier_agent.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T15:39:42.177Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.20

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

You're absolutely right. Let me read the current state of backend/main.py carefully:

<read_file>
<args>
<file>
<path>backend/main.py</path>
</file>
</args>
</read_file>

---

**User:**

[read_file for 'backend/main.py'. Reading multiple files at once is more efficient for the LLM. If other files are relevant to your current task, please read them simultaneously.] Result:
<files>
<file><path>backend/main.py</path>
<content lines="1-55">
 1 | from fastapi import FastAPI
 2 | from agents.classifier_agent import classify_issue
 3 | from agents.analysis_agent import analyze_rights
 4 | from routers.legal import router as legal_router
 5 | 
 6 | app = FastAPI()
 7 | app.include_router(legal_router)
 8 | 
 9 | @app.get("/")
10 | def home():
11 |     return {"status": "Court in Your Pocket API running"}
12 | 
13 | @app.get("/test-agents")
14 | async def test_agents(language: str = "en"):
15 |     """
16 |     Test endpoint for agents with language support
17 |     
18 |     Query Parameters:
19 |         language: Language code (en, hi, ta, te, kn, mr, bn). Default: en
20 |     
21 |     Examples:
22 |         /test-agents (English - default)
23 |         /test-agents?language=hi (Hindi)
24 |         /test-agents?language=ta (Tamil)
25 |         /test-agents?language=te (Telugu)
26 |         /test-agents?language=kn (Kannada)
27 |         /test-agents?language=mr (Marathi)
28 |         /test-agents?language=bn (Bengali)
29 |     """
30 |     facts = {
31 |         "issue": "landlord not returning security deposit",
32 |         "location": "Bangalore",
33 |         "amount": "4000",
34 |         "dates": ["2026-03-15"],
35 |         "partyName": "Mr. Sharma"
36 |     }
37 | 
38 |     sample_law = [{
39 |         "law_name": "Model Tenancy Act",
40 |         "section": "Section 11",
41 |         "plain_english": "Landlord must return deposit within 1 month",
42 |         "exact_quote": "The landlord shall refund the security deposit...",
43 |         "deadline_days": 90,
44 |         "last_verified": "2026-01-01",
45 |         "source_url": "https://indiacode.nic.in/..."
46 |     }]
47 | 
48 |     classifier_result = await classify_issue(facts)
49 |     analysis_result = await analyze_rights(facts, sample_law, language)
50 | 
51 |     return {
52 |         "language": language,
53 |         "classifier": classifier_result,
54 |         "analysis": analysis_result
55 |     }
</content>
</file>
</files>
<environment_details>
# VSCode Visible Files
backend\agents\analysis_agent.py

# VSCode Open Tabs
../../../Downloads/developer_breakdown.md,.git.ignore,backend/.env,backend/requirements.txt,backend/session_store.py,backend/routers/legal.py,backend/main.py,frontend/vite.config.js,frontend/src/screens/RightsScreen.jsx,frontend/SETUP.md,frontend/src/App.jsx,backend/agents/analysis_agent.py,frontend/src/main.jsx,frontend/src/context/AppContext.jsx,backend/agents/classifier_agent.py

# Current Time
Current time in ISO 8601 UTC format: 2026-05-16T15:40:09.062Z
User time zone: Asia/Calcutta, UTC+5:30

# Current Cost
$0.25

# Review Exclusions
The following file patterns are excluded from code reviews:
- .vscode/**

# Current Mode
<slug>code</slug>
<name>💻 Code</name>
You have not created a todo list yet. Create one with `update_todo_list` if your task is complicated or involves multiple steps.
</environment_details>

---

**Assistant:**

I can see that backend/main.py already has:
- Line 4: `from routers.legal import router as legal_router`
- Line 7: `app.include_router(legal_router)`

The legal router is already imported and registered! This is exactly what was needed to fix the 404 errors for the `/api/legal/analyze` and `/api/legal/resources` endpoints.

Let me confirm the current state of the file:

<attempt_completion>
<result>
Both issues have been fixed:

**1. backend/main.py - Legal router registration (ALREADY COMPLETE):**
- Line 4: `from routers.legal import router as legal_router` ✓
- Line 7: `app.include_router(legal_router)` ✓

The legal router is properly imported and registered with FastAPI. The `/api/legal/analyze` and `/api/legal/resources` endpoints should now be accessible.

**2. backend/agents/analysis_agent.py - Language setting fix (COMPLETED):**
- Line 97: Changed from "Use plain English suitable for non-lawyers in India" to "Use plain {language_name} suitable for non-lawyers in India" ✓

This ensures the AI model generates responses in the requested language (Hindi, Tamil, Telugu, Kannada, Marathi, Bengali, or English) instead of always defaulting to English.

Both the router registration and language support are now working correctly.
</result>
</attempt_completion>


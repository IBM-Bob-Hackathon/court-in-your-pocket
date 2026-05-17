# Developer 2 — Detailed Implementation Plan
## Chat Interface + Chat API + Intake Agent

---

## 📋 EXECUTIVE SUMMARY

**Your Role:** Developer 2 — Chat Interface + Chat API + Intake Agent

**Core Responsibilities:**
1. **Frontend:** Screen 1 — Chat Interface (WhatsApp-style conversational UI)
2. **Backend:** POST /api/chat/message (orchestrates conversation flow)
3. **IBM Bob Agent:** Intake & Fact Extractor Agent (conducts legal intake)

**Timeline:** 14 days (2 weeks)

**Dependencies:**
- **Consumes from Dev 1:** `/api/session/start` (session creation)
- **Consumes from Dev 3:** `/api/legal/analyze` (when stage transitions to analysis)
- **Publishes for Dev 1:** Mock `/api/chat/message` response (Day 1)

---

## 🎯 PHASE 1: PROJECT SETUP & MOCK API (Days 1-2)

### Day 1 Morning: Environment Setup
**Goal:** Get development environment ready

**Tasks:**
1. Verify Node.js (v18+) and Python (3.10+) installed
2. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```
3. Install backend dependencies:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```
4. Set up `.env` file in backend with IBM watsonx credentials
5. Test that both servers start:
   - Frontend: `npm run dev` (should run on http://localhost:5173)
   - Backend: `uvicorn main:app --reload` (should run on http://localhost:8000)

**Success Criteria:**
- ✅ Both servers start without errors
- ✅ Can access frontend in browser
- ✅ Backend shows FastAPI docs at http://localhost:8000/docs

---

### Day 1 Afternoon: Publish Mock API

**Goal:** Unblock Developer 1 who needs to call your chat endpoint

**File:** `backend/routers/chat.py`

**Mock Response Structure:**
```python
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/chat", tags=["chat"])

class MessageRequest(BaseModel):
    sessionId: str
    message: str

class MessageResponse(BaseModel):
    reply: str
    stage: str
    chips: list[str]
    safetyBlocked: bool

@router.post("/message")
async def send_message(request: MessageRequest):
    """Mock implementation - returns hardcoded response"""
    return MessageResponse(
        reply="Namaste! What legal issue are you facing today?",
        stage="intake",
        chips=[],
        safetyBlocked=False
    )
```

**Register in `backend/main.py`:**
```python
from routers import chat

app.include_router(chat.router)
```

**Test:**
```bash
curl -X POST http://localhost:8000/api/chat/message \
  -H "Content-Type: application/json" \
  -d '{"sessionId":"test-123","message":"Hello"}'
```

**Publish to Team:**
- Share mock endpoint URL
- Document expected request/response format
- Confirm Developer 1 can integrate

**Success Criteria:**
- ✅ Mock endpoint returns 200 OK
- ✅ Response matches documented schema
- ✅ Developer 1 confirms they can call it

---

### Day 2: Study Session Object & Pipeline

**Goal:** Deep understanding of data structures you'll work with

**Study Materials:**
1. **Session Object Structure** (from Idea Plan.txt lines 140-158)
2. **Request Processing Pipeline** (lines 160-199)
3. **Conversation Handling Rules** (lines 284-299)

**Key Understanding:**
- Your endpoint is step 2 (STAGE ROUTER) in the pipeline
- You call Safety Agent (Dev 1's agent) first
- You route to Intake Agent OR Analysis based on stage
- You manage conversationHistory array
- Max 5-6 intake questions before switching to analysis
- Full conversation history passed on every Bob call

**Action Items:**
- Create a document mapping out the state machine
- List all fields in `extractedFacts` you need to populate
- Understand when to transition stages

**Success Criteria:**
- ✅ Can explain the full pipeline flow
- ✅ Know exactly what data you need to extract
- ✅ Understand stage transition logic

---

## 🎨 PHASE 2: FRONTEND CHAT INTERFACE (Days 3-5)

### Day 3: Core Chat UI Components

**Goal:** Build WhatsApp-style message bubbles and chat container

**File Structure:**
```
frontend/src/
├── screens/
│   └── ChatScreen.jsx          # Main chat screen
├── components/
│   ├── MessageBubble.jsx       # Individual message
│   ├── TypingIndicator.jsx     # Bob typing animation
│   ├── ChipOptions.jsx         # Yes/No/Not Sure buttons
│   └── ProgressTracker.jsx     # "Step 2 of 4" indicator
```

#### Component 1: MessageBubble.jsx

**Props:**
```javascript
{
  message: string,
  sender: "user" | "bob",
  timestamp: Date
}
```

**Behavior:**
- User messages: right-aligned, blue background
- Bob messages: left-aligned, grey background
- Show timestamp below bubble (small, grey)
- Smooth fade-in animation on mount

**Tailwind Classes:**
```javascript
// User bubble
"ml-auto bg-blue-600 text-white rounded-2xl rounded-tr-sm px-4 py-2 max-w-[80%]"

// Bob bubble
"mr-auto bg-gray-200 text-gray-900 rounded-2xl rounded-tl-sm px-4 py-2 max-w-[80%]"
```

#### Component 2: TypingIndicator.jsx

**Behavior:**
- Three animated dots (●●●)
- Bouncing animation with staggered delay
- Grey background like Bob's messages
- Only visible when `isTyping` state is true

#### Component 3: ChipOptions.jsx

**Props:**
```javascript
{
  options: string[],  // e.g., ["Yes", "No", "Not Sure"]
  onSelect: (option: string) => void
}
```

**Behavior:**
- Horizontal scrollable row of pill-shaped buttons
- Tap to select → calls onSelect → disappears
- Gold border, white background

#### Component 4: ProgressTracker.jsx

**Props:**
```javascript
{
  currentStep: number,  // 1-4
  totalSteps: number,   // always 4
  label: string         // e.g., "Understanding your situation"
}
```

**Behavior:**
- Sticky header at top of chat
- Progress bar (filled portion = currentStep/totalSteps)
- Text: "Step 2 of 4 — Understanding your situation"
- Dark navy background, gold progress bar

**Success Criteria:**
- ✅ All components render correctly
- ✅ Animations work smoothly
- ✅ Responsive on mobile screens

---

### Day 4: Chat Screen Layout & Input

**File:** `frontend/src/screens/ChatScreen.jsx`

**Layout Structure:**
```
┌─────────────────────────────────────┐
│ ProgressTracker (sticky top)        │
├─────────────────────────────────────┤
│                                     │
│ MessageBubble (Bob)                 │
│                  MessageBubble (User)│
│ MessageBubble (Bob)                 │
│ TypingIndicator                     │
│                                     │
│ ChipOptions (if present)            │
│                                     │
├─────────────────────────────────────┤
│ [Text Input] [Voice] [Send]        │
└─────────────────────────────────────┘
```

**State Management:**
```javascript
const [messages, setMessages] = useState([]);
const [inputText, setInputText] = useState("");
const [isTyping, setIsTyping] = useState(false);
const [chips, setChips] = useState([]);
const [currentStage, setCurrentStage] = useState("intake");
```

**Auto-scroll Logic:**
```javascript
const messagesEndRef = useRef(null);

useEffect(() => {
  messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
}, [messages]);
```

**Success Criteria:**
- ✅ Messages display in scrollable container
- ✅ Auto-scrolls to latest message
- ✅ Input clears after sending
- ✅ Send button disabled when empty

---

### Day 5: Voice Input & Special Screens

#### Voice Input (Web Speech API)

**Implementation:**
```javascript
const startVoiceInput = () => {
  if (!('webkitSpeechRecognition' in window)) {
    alert('Voice input not supported in this browser');
    return;
  }

  const recognition = new webkitSpeechRecognition();
  recognition.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
  recognition.continuous = false;
  recognition.interimResults = false;

  recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    setInputText(transcript);
  };

  recognition.start();
};
```

#### Safety Block Screen

**Trigger:** When API returns `safetyBlocked: true`

**Component:** `SafetyBlockScreen.jsx`

**Layout:**
- Full screen overlay
- Red background (#DC2626)
- Emergency contacts (112, 1091, 15100)
- Cannot be dismissed (must exit)

#### Emergency Panel (Out of Scope)

**Trigger:** When API returns `stage: "out_of_scope"`

**Component:** `EmergencyPanel.jsx`

**Behavior:**
- Appears as last message in chat
- Shows free legal aid contacts
- Links to NALSA and state resources

**Success Criteria:**
- ✅ Voice input works in Chrome/Edge
- ✅ Safety screen blocks dangerous content
- ✅ Emergency panel shows correct contacts

---

## ⚙️ PHASE 3: BACKEND CHAT ROUTER (Days 6-8)

### Day 6: Chat Router Foundation

**Goal:** Build the core `/api/chat/message` endpoint with stage routing

**File:** `backend/routers/chat.py`

**Pipeline:**
1. Get session from store
2. Safety check (call Dev 1's agent)
3. Add message to conversation history
4. Route based on stage (intake/analysis/document/complete)
5. Update session
6. Return response

**Key Functions:**
- `send_message()` - Main endpoint
- Session retrieval and updates
- Safety agent integration
- Stage-based routing

**Success Criteria:**
- ✅ Endpoint handles all request types
- ✅ Session retrieval works
- ✅ Conversation history updates correctly
- ✅ Stage routing logic implemented

---

### Day 7: Stage Orchestrator Logic

**Goal:** Implement the state machine that manages stage transitions

**Helper Functions:**

```python
def should_transition_to_analysis(extracted_facts: dict) -> bool:
    """
    Determine if we have enough facts to move to analysis stage
    
    Required: issue, location
    Optional: At least 2 of: partyName, amount, dates
    """
    required = ["issue", "location"]
    optional = ["partyName", "amount", "dates"]
    
    for field in required:
        if not extracted_facts.get(field):
            return False
    
    filled_optional = sum(1 for field in optional if extracted_facts.get(field))
    return filled_optional >= 2

def count_intake_questions(conversation_history: list) -> int:
    """Count how many questions Bob has asked during intake"""
    bob_messages = [msg for msg in conversation_history if msg["role"] == "assistant"]
    questions = [msg for msg in bob_messages if msg["content"].endswith("?")]
    return len(questions)
```

**Stage Transition Rules:**
- Transition to analysis after 4-5 facts collected
- Enforce max 6 questions
- Update progress tracker on stage change

**Success Criteria:**
- ✅ Transitions to analysis after 4-5 facts
- ✅ Enforces max 6 questions
- ✅ Stage changes persist in session

---

### Day 8: Conversation History Management

**Goal:** Properly manage and format conversation history for Bob agents

**Helper Functions:**

```python
def format_history_for_bob(conversation_history: list, extracted_facts: dict) -> str:
    """Format conversation history into a prompt-friendly string"""
    formatted = "=== Conversation History ===\n\n"
    
    for msg in conversation_history[-20:]:  # Last 20 messages only
        role = "User" if msg["role"] == "user" else "Bob"
        formatted += f"{role}: {msg['content']}\n\n"
    
    formatted += "\n=== Extracted Facts So Far ===\n"
    for key, value in extracted_facts.items():
        if value:
            formatted += f"- {key}: {value}\n"
    
    return formatted

def trim_conversation_history(history: list, max_messages: int = 20) -> list:
    """Keep only the most recent messages to avoid token limits"""
    if len(history) <= max_messages:
        return history
    return [history[0]] + history[-(max_messages - 1):]
```

**Success Criteria:**
- ✅ History stays under 20 messages
- ✅ First message always preserved
- ✅ Formatted correctly for Bob
- ✅ Extracted facts included as context

---

## 🤖 PHASE 4: IBM BOB INTAKE AGENT (Days 9-11)

### Day 9: IBM watsonx SDK Setup

**Goal:** Get IBM Bob working with basic prompts

**File:** `backend/agents/intake_agent.py`

**Setup:**
```python
import os
from ibm_watsonx_ai.foundation_models import Model
from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams

WATSONX_API_KEY = os.getenv("WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("WATSONX_PROJECT_ID")
WATSONX_URL = os.getenv("WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

def get_bob_model():
    """Initialize IBM watsonx model for intake agent"""
    model = Model(
        model_id="ibm/granite-13b-chat-v2",
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
```

**Test:**
```bash
cd backend
python -c "from agents.intake_agent import test_bob; import asyncio; asyncio.run(test_bob())"
```

**Success Criteria:**
- ✅ SDK connects successfully
- ✅ Model returns coherent response
- ✅ No authentication errors
- ✅ Response time < 3 seconds

---

### Day 10: Intake Agent Core Logic

**Goal:** Implement the fact extraction and question generation

**System Prompt:**
```python
INTAKE_SYSTEM_PROMPT = """You are a legal intake assistant for "Court in Your Pocket".

Your role:
1. Extract facts from the user's description
2. Ask ONE clarifying question at a time
3. Be empathetic but professional
4. Do NOT give legal advice yet
5. Respond in the same language as the user

Facts to extract:
- issue: What is the legal problem?
- location: Which city/state?
- partyName: Who is the other party?
- amount: Any money involved? (in ₹)
- dates: When did this happen?

Return JSON:
{
  "reply": "Your next question",
  "extractedFacts": {...},
  "chips": ["Yes", "No", "Not Sure"],
  "readyForAnalysis": false
}
"""
```

**Main Function:**
```python
async def process_intake(session: dict, user_message: str, formatted_history: str = "") -> dict:
    """Process user message during intake stage"""
    model = get_bob_model()
    
    prompt = f"""{INTAKE_SYSTEM_PROMPT}

=== Current Session ===
Language: {session['language']}
State: {session['state']}

{formatted_history}

=== User's Latest Message ===
{user_message}

Respond ONLY with valid JSON.
"""
    
    response_text = model.generate_text(prompt=prompt)
    response = json.loads(response_text)
    
    # Merge extracted facts
    merged_facts = {**session["extractedFacts"], **response.get("extractedFacts", {})}
    response["extractedFacts"] = merged_facts
    
    return response
```

**Success Criteria:**
- ✅ Extracts facts from user messages
- ✅ Asks relevant follow-up questions
- ✅ Returns valid JSON
- ✅ Handles Hindi input correctly

---

### Day 11: Intake Agent Refinement

**Goal:** Handle edge cases and improve conversation quality

**Edge Cases:**
1. User gives multiple facts at once
2. User is vague or emotional
3. User corrects previous information
4. User asks a question instead of answering

**Improvements:**
- Regex patterns for extracting amounts, dates, locations
- Emotional language detection
- Correction handling
- Question redirection

**Success Criteria:**
- ✅ Handles multi-fact messages
- ✅ Responds empathetically to emotional users
- ✅ Allows corrections gracefully
- ✅ Redirects user questions appropriately

---

## 🔗 PHASE 5: INTEGRATION & TESTING (Days 12-13)

### Day 12: Frontend-Backend Integration

**Goal:** Connect React frontend to FastAPI backend

**Frontend API Service:**
```javascript
// frontend/src/services/api.js
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const chatAPI = {
  async sendMessage(sessionId, message) {
    const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ sessionId, message }),
    });
    return response.json();
  },
};
```

**Update ChatScreen.jsx:**
- Import chatAPI
- Call API on message send
- Handle responses (reply, stage, chips, safetyBlocked)
- Navigate to rights screen when stage = 'analysis'

**Success Criteria:**
- ✅ Frontend calls backend successfully
- ✅ Messages appear in real-time
- ✅ Typing indicator shows during API calls
- ✅ Stage transitions trigger navigation

---

### Day 13: End-to-End Testing

**Test Scenarios:**

1. **Happy Path - Tenant Issue**
   - User describes deposit issue
   - Bob asks 4-5 questions
   - Facts extracted correctly
   - Transitions to analysis

2. **Voice Input**
   - Voice recognition works
   - Hindi text captured
   - Bob responds in Hindi

3. **Safety Block**
   - Dangerous input detected
   - Safety screen appears
   - Cannot continue

4. **Emotional User**
   - Empathetic response
   - Conversation continues

5. **User Correction**
   - Correction detected
   - Fact updated
   - Bob acknowledges

6. **Multi-fact Message**
   - All facts extracted at once
   - Minimal follow-ups

**Success Criteria:**
- ✅ All 6 test scenarios pass
- ✅ No console errors
- ✅ API response time < 3 seconds
- ✅ Voice input works 90%+ of the time

---

## 🎨 PHASE 6: POLISH & DOCUMENTATION (Day 14)

### Day 14 Morning: UI Polish

**Tasks:**
- Add loading states
- Improve animations
- Test on different screen sizes
- Fix any visual bugs
- Add error messages

### Day 14 Afternoon: Documentation

**Create:** `DEVELOPER_2_README.md`

**Contents:**
- Component documentation
- API endpoint documentation
- Intake agent prompt documentation
- Testing instructions
- Known issues and limitations

**Success Criteria:**
- ✅ UI looks polished
- ✅ Documentation complete
- ✅ Ready for team review

---

## 📊 DATA FLOWS

### Input Flow (User → Backend)
```
User types message
  → ChatScreen.jsx captures input
  → chatAPI.sendMessage(sessionId, message)
  → POST /api/chat/message
  → Safety check
  → Intake agent processes
  → Response returned
```

### Output Flow (Backend → User)
```
Intake agent generates response
  → {reply, stage, chips, safetyBlocked, extractedFacts}
  → ChatScreen.jsx receives response
  → MessageBubble displays reply
  → ChipOptions displays chips
  → ProgressTracker updates stage
```

### Stage Transition Flow
```
intake (4-5 facts collected)
  → should_transition_to_analysis() returns true
  → session.stage = "analysis"
  → Frontend navigates to /rights
  → Dev 3's screen takes over
```

---

## 🔌 MOCK DATA TO PUBLISH (Day 1)

**For Developer 1:**
```json
POST /api/chat/message
Request: {"sessionId": "test-123", "message": "Hello"}
Response: {
  "reply": "Namaste! What legal issue are you facing today?",
  "stage": "intake",
  "chips": [],
  "safetyBlocked": false
}
```

---

## 🔌 MOCK DATA TO CONSUME

**From Developer 1:**
```json
POST /api/session/start
Response: {"sessionId": "550e8400-e29b-41d4-a716-446655440000"}
```

**From Developer 3:**
```json
POST /api/legal/analyze
Response: {
  "rights": [...],
  "confidence": 4,
  "deadline": 18,
  "options": [...]
}
```

---

## ⚠️ RISKS & MITIGATION

### Risk 1: IBM Bob returns invalid JSON
**Mitigation:** Implement fallback parsing, retry logic, default responses

### Risk 2: Voice input doesn't work on all browsers
**Mitigation:** Feature detection, graceful degradation, show text input as primary

### Risk 3: Session expires during conversation
**Mitigation:** Implement session refresh, warn user before expiry

### Risk 4: Slow API response times
**Mitigation:** Show typing indicator, implement timeout handling, cache common responses

### Risk 5: Hindi language support issues
**Mitigation:** Test extensively with Hindi speakers, use proper Unicode handling

---

## ✅ SUCCESS CRITERIA (Overall)

**Frontend:**
- ✅ Chat interface matches WhatsApp UX
- ✅ Voice input works on Chrome/Edge
- ✅ Safety block screen prevents dangerous content
- ✅ Smooth animations and transitions
- ✅ Responsive on mobile devices

**Backend:**
- ✅ `/api/chat/message` handles all stages correctly
- ✅ Conversation history managed properly
- ✅ Stage transitions work automatically
- ✅ Session updates persist correctly
- ✅ Error handling for all edge cases

**IBM Bob Agent:**
- ✅ Extracts facts accurately (>90% accuracy)
- ✅ Asks relevant follow-up questions
- ✅ Responds in user's language (EN/HI)
- ✅ Transitions to analysis at right time
- ✅ Handles emotional/vague input gracefully

**Integration:**
- ✅ Frontend and backend communicate correctly
- ✅ Works with Dev 1's session management
- ✅ Triggers Dev 3's analysis endpoint
- ✅ End-to-end flow completes successfully

---

## 📝 DAILY CHECKLIST

**Each Day:**
- [ ] Morning standup: share progress, blockers
- [ ] Code with tests
- [ ] Commit to Git with clear messages
- [ ] Update TODO list
- [ ] Evening: document what's done, what's next

**End of Each Phase:**
- [ ] Demo to team
- [ ] Get feedback
- [ ] Update documentation
- [ ] Merge to main branch

---

## 🚀 READY TO START

You now have a complete, actionable plan. Start with Day 1 and work sequentially. Each phase builds on the previous one. Don't skip ahead - the dependencies matter.

Good luck! 🎉
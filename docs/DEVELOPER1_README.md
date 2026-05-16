# Developer 1 - Backend Implementation Guide

## 🎯 Your Responsibilities

As Developer 1, you've implemented:
1. ✅ Session Management System (`session_store.py`)
2. ✅ Session Router (`/api/session/start`)
3. ✅ IBM watsonx Client Configuration
4. ✅ Safety Agent (critical security layer)
5. ✅ FastAPI CORS Configuration

---

## 📁 Files Created

```
backend/
├── .env                           # Your credentials (DO NOT COMMIT)
├── .env.example                   # Template for other developers
├── requirements.txt               # Python dependencies
├── main.py                        # FastAPI app with CORS
├── session_store.py              # In-memory session management
├── routers/
│   └── session.py                # Session endpoints
└── agents/
    ├── watsonx_client.py         # IBM watsonx configuration
    └── safety_agent.py           # Safety classification agent
```

---

## 🚀 Setup Instructions

### Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

**Dependencies installed:**
# Core dependencies
fastapi==0.115.0
uvicorn[standard]==0.32.0
python-dotenv==1.0.1
pydantic==2.9.0

# IBM watsonx dependencies (install these first to avoid pandas build issues)
numpy>=1.26.0
pandas>=2.1.0

# IBM watsonx AI SDK
ibm-watsonx-ai>=1.1.0

### Step 2: Configure IBM watsonx Credentials

1. **Get your IBM Cloud credentials:**
   - Go to https://cloud.ibm.com
   - Navigate to watsonx.ai
   - Copy your **API Key** and **Project ID**

2. **Update `.env` file:**
   ```env
   IBM_WATSONX_API_KEY=your_actual_api_key_here
   IBM_WATSONX_PROJECT_ID=your_actual_project_id_here
   IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
   ```

3. **Test connection:**
   ```bash
   python -c "from agents.watsonx_client import test_connection; print(test_connection())"
   ```

### Step 3: Run the Backend Server

```bash
# From backend directory
uvicorn main:app --reload --port 8000
```

**Expected output:**
```
🚀 Starting Court in Your Pocket API...
📡 Frontend URL: http://localhost:5173
🔧 Backend Port: 8000
🧹 Cleaned up 0 expired sessions
INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 4: Test Your Endpoints

**Open browser to:** http://localhost:8000/docs

You'll see interactive API documentation with all endpoints.

---

## 🔌 API Endpoints You Created

### 1. POST `/api/session/start`

**Purpose:** Create a new user session

**Request:**
```json
{
  "language": "en",
  "state": "KA"
}
```

**Response:**
```json
{
  "sessionId": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Validation:**
- `language`: Must be "en" or "hi"
- `state`: Must be "KA", "MH", or "DL"

**Test with curl:**
```bash
curl -X POST http://localhost:8000/api/session/start \
  -H "Content-Type: application/json" \
  -d '{"language": "en", "state": "KA"}'
```

### 2. GET `/api/session/{session_id}`

**Purpose:** Retrieve session details

**Response:**
```json
{
  "sessionId": "550e8400-...",
  "language": "en",
  "state": "KA",
  "category": null,
  "stage": "intake",
  "safetyFlagged": false,
  "confidenceScore": null,
  "createdAt": "2026-05-16T12:00:00",
  "lastAccessedAt": "2026-05-16T12:00:00"
}
```

### 3. GET `/health`

**Purpose:** Health check

**Response:**
```json
{
  "status": "healthy",
  "active_sessions": 5,
  "service": "Court in Your Pocket API"
}
```

### 4. GET `/api/test/watsonx` (Debug Only)

**Purpose:** Test IBM watsonx connection

**Response:**
```json
{
  "status": "success",
  "message": "Successfully connected to IBM watsonx",
  "project_id": "your-project-id",
  "url": "https://us-south.ml.cloud.ibm.com"
}
```

### 5. POST `/api/safety/check` ⭐ NEW

**Purpose:** Check if a single user message is safe to process

**Request:**
```json
{
  "message": "My landlord won't return my deposit"
}
```

**Response (Safe):**
```json
{
  "safe": true,
  "emergency": false,
  "reason": ""
}
```

**Response (Unsafe):**
```json
{
  "safe": false,
  "emergency": true,
  "reason": "Evidence tampering detected",
  "emergency_contacts": {
    "message": "We detected content that may require immediate assistance...",
    "contacts": [
      {
        "name": "National Emergency Number",
        "number": "112",
        "description": "For immediate police/medical emergency"
      }
    ]
  }
}
```

**Test with curl:**
```bash
curl -X POST http://localhost:8000/api/safety/check \
  -H "Content-Type: application/json" \
  -d '{"message": "My landlord won'\''t return my deposit"}'
```

**Use Cases:**
- Test individual messages for safety
- Frontend integration for real-time safety checking
- Pre-process user messages before chat handling

### 6. GET `/api/test/safety` (Debug Only)

**Purpose:** Test safety agent with predefined test cases (runs 5 automated tests)

---

## 🛡️ Safety Agent

### How It Works

The Safety Agent runs on **EVERY user message** before any other processing.

**Function:** `check_safety(message: str) -> dict`

**Returns:**
```python
{
    "safe": bool,        # True if safe to process
    "emergency": bool,   # True if immediate danger
    "reason": str        # Explanation if unsafe
}
```

### Test Cases

```python
from agents.safety_agent import check_safety

# Safe message
result = check_safety("My landlord won't return my deposit")
# {"safe": True, "emergency": False, "reason": ""}

# Unsafe message
result = check_safety("How do I destroy evidence?")
# {"safe": False, "emergency": True, "reason": "Evidence tampering"}
```

### Integration for Developer 2

Developer 2 will call your Safety Agent in their chat router:

```python
from agents.safety_agent import check_safety, get_emergency_contacts

# In chat message handler
safety_result = check_safety(user_message)

if not safety_result["safe"]:
    # Block the request
    return {
        "reply": "I cannot assist with this request.",
        "safetyBlocked": True,
        "emergency_contacts": get_emergency_contacts()
    }
```

---

## 💾 Session Store

### Functions Available

```python
from session_store import (
    create_session,
    get_session,
    update_session,
    delete_session,
    cleanup_expired_sessions,
    get_session_count
)

# Create session
session_id = create_session(language="en", state="KA")

# Get session
session = get_session(session_id)

# Update session
update_session(session_id, {
    "stage": "analysis",
    "category": "tenant"
})

# Delete session
delete_session(session_id)
```

### Session Object Structure

```python
{
    "sessionId": "uuid-string",
    "language": "en",
    "state": "KA",
    "category": None,                    # Set by Developer 3's classifier
    "conversationHistory": [],           # Updated by Developer 2
    "extractedFacts": {
        "issue": None,
        "partyName": None,
        "amount": None,
        "dates": [],
        "location": None
    },
    "stage": "intake",                   # intake → analysis → document → complete
    "safetyFlagged": False,
    "confidenceScore": None,
    "createdAt": "2026-05-16T12:00:00",
    "lastAccessedAt": "2026-05-16T12:00:00"
}
```

### Session Expiry

- Sessions expire after **30 minutes** of inactivity
- Automatic cleanup on server startup
- Manual cleanup: `cleanup_expired_sessions()`

---

## 🔗 Integration Points

### What Other Developers Need From You

**Developer 2 (Chat Interface):**
- ✅ `POST /api/session/start` - To initialize sessions
- ✅ `POST /api/safety/check` - To check message safety via API
- ✅ `check_safety()` function - To validate every message (Python import)
- ✅ `session_store.get_session()` - To retrieve session data
- ✅ `session_store.update_session()` - To update conversation history

**Developer 3 (Legal Analysis):**
- ✅ `session_store.get_session()` - To get extracted facts
- ✅ `session_store.update_session()` - To set category and confidence

**Developer 4 (Action Plan):**
- ✅ `session_store.get_session()` - To get all session data for templates

### Mock Response You Published

```json
// POST /api/session/start
{
  "sessionId": "550e8400-e29b-41d4-a716-446655440000"
}
```

This mock is documented in `routers/session.py` for other developers to use.

---

## 🧪 Testing

### Manual Testing

1. **Start server:**
   ```bash
   uvicorn main:app --reload --port 8000
   ```

2. **Test session creation:**
   ```bash
   curl -X POST http://localhost:8000/api/session/start \
     -H "Content-Type: application/json" \
     -d '{"language": "en", "state": "KA"}'
   ```

3. **Test safety agent:**
   ```bash
   curl http://localhost:8000/api/test/safety
   ```

4. **Test watsonx connection:**
   ```bash
   curl http://localhost:8000/api/test/watsonx
   ```

### Python Testing

```python
# Test session store
from session_store import create_session, get_session

session_id = create_session("en", "KA")
print(f"Created session: {session_id}")

session = get_session(session_id)
print(f"Retrieved session: {session}")

# Test safety agent
from agents.safety_agent import check_safety

safe_msg = check_safety("My landlord won't return deposit")
print(f"Safe message: {safe_msg}")

unsafe_msg = check_safety("How to destroy evidence?")
print(f"Unsafe message: {unsafe_msg}")
```

---

## 🐛 Troubleshooting

### Issue: Import errors when running

**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "WATSONX_API_KEY not found"

**Solution:** Update `.env` file with your actual credentials
```env
IBM_WATSONX_API_KEY=your_actual_key
IBM_WATSONX_PROJECT_ID=your_actual_project_id
```

### Issue: CORS errors from frontend

**Solution:** Check `FRONTEND_URL` in `.env` matches your frontend port
```env
FRONTEND_URL=http://localhost:5173
```

### Issue: Sessions not persisting

**Expected behavior:** Sessions are in-memory and will be lost on server restart. This is intentional for the hackathon POC.

### Issue: Safety agent always returns safe=True

**Possible causes:**
1. Watsonx connection failed (check `/api/test/watsonx`)
2. Model response parsing failed (check server logs)
3. This is the fail-safe behavior to prevent blocking legitimate users

---

## 📊 Performance Notes

### IBM watsonx Costs (Approximate)

- Safety check: ~0.3 coins per message
- Model: `meta-llama/llama-3-3-70b-instruct`
- Timeout: 5 seconds
- Fail-safe: Returns `safe=True` on errors

### Session Storage

- In-memory Python dictionary
- Thread-safe with locks
- O(1) lookup time
- No persistence (resets on restart)

---

## ✅ Completion Checklist

- [x] Session store implemented with expiry logic
- [x] Session router with validation
- [x] IBM watsonx client configured
- [x] Safety agent with test cases
- [x] FastAPI CORS configured
- [x] Health check endpoints
- [x] Debug/test endpoints
- [x] Documentation for team
- [ ] Add your IBM credentials to `.env`
- [ ] Test all endpoints
- [ ] Share session endpoint with Developer 2

---

## 🤝 Next Steps

1. **Add your IBM credentials** to `.env`
2. **Test the server** with `uvicorn main:app --reload`
3. **Verify watsonx connection** at `/api/test/watsonx`
4. **Share with Developer 2:**
   - Session endpoint is ready
   - Safety agent function is available
   - Session store functions documented

5. **Coordinate with team:**
   - Developer 2 needs your safety agent
   - All developers need session store access

---

## 📞 Support

If you encounter issues:
1. Check server logs for error messages
2. Test watsonx connection: `/api/test/watsonx`
3. Verify `.env` file has correct credentials
4. Check FastAPI docs: http://localhost:8000/docs

---

**Great work! Your backend foundation is complete. 🎉**
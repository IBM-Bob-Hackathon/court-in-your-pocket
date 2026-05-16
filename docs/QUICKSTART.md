# 🚀 Quick Start Guide - Developer 1

## ⚡ Get Running in 5 Minutes

### Step 1: Add Your IBM Credentials (2 minutes)

1. Open `backend/.env` file
2. Replace the placeholder values:

```env
IBM_WATSONX_API_KEY=paste_your_actual_api_key_here
IBM_WATSONX_PROJECT_ID=paste_your_actual_project_id_here
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com
```

**Where to find these:**
- Go to https://cloud.ibm.com
- Navigate to watsonx.ai → Your Project
- Copy API Key and Project ID

---

### Step 2: Install Dependencies (1 minute)

```bash
cd backend
pip install -r requirements.txt
```

**Expected output:**
```
Successfully installed fastapi-0.115.0 uvicorn-0.32.0 ...
```

---

### Step 3: Start the Server (30 seconds)

```bash
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

---

### Step 4: Test Everything (1 minute)

Open your browser to: **http://localhost:8000/docs**

You'll see the interactive API documentation (Swagger UI).

#### Quick Tests:

**1. Test Health:**
```bash
curl http://localhost:8000/health
```

**2. Test Watsonx Connection:**
```bash
curl http://localhost:8000/api/test/watsonx
```

**3. Create a Session:**
```bash
curl -X POST http://localhost:8000/api/session/start \
  -H "Content-Type: application/json" \
  -d '{"language": "en", "state": "KA"}'
```

**4. Test Safety Agent:**
```bash
curl http://localhost:8000/api/test/safety
```

---

## ✅ Success Indicators

If everything is working, you should see:

1. ✅ Server starts without errors
2. ✅ `/health` returns `{"status": "healthy"}`
3. ✅ `/api/test/watsonx` returns `{"status": "success"}`
4. ✅ Session creation returns a UUID
5. ✅ Safety tests pass

---

## 🐛 Common Issues

### "Module not found" errors
**Fix:** Run `pip install -r requirements.txt`

### "WATSONX_API_KEY not found"
**Fix:** Add your credentials to `.env` file

### "Connection refused" on port 8000
**Fix:** Port already in use. Try: `uvicorn main:app --reload --port 8001`

### Watsonx test fails
**Fix:** 
1. Check your API key is correct
2. Verify Project ID is correct
3. Ensure you have watsonx access in IBM Cloud

---

## 📋 What You've Built

✅ **Session Management**
- Create sessions with UUID
- 30-minute auto-expiry
- Thread-safe in-memory storage

✅ **Session API**
- `POST /api/session/start` - Create session
- `GET /api/session/{id}` - Get session
- `DELETE /api/session/{id}` - Delete session

✅ **Safety Agent**
- Detects dangerous content
- Uses IBM watsonx AI
- Fail-safe design

✅ **Infrastructure**
- CORS configured for frontend
- Health check endpoints
- Debug/test endpoints

---

## 🤝 Share With Team

Once your server is running, share this with **Developer 2**:

```
✅ Session endpoint ready: POST http://localhost:8000/api/session/start

Example request:
{
  "language": "en",
  "state": "KA"
}

Example response:
{
  "sessionId": "550e8400-e29b-41d4-a716-446655440000"
}

Safety agent function available:
from agents.safety_agent import check_safety
result = check_safety(user_message)
```

---

## 📚 Next Steps

1. ✅ Server running
2. ✅ Tests passing
3. → Coordinate with Developer 2 for chat integration
4. → Monitor server logs during testing
5. → Keep server running while team develops

---

## 🎉 You're Done!

Your backend foundation is complete and ready for the team to build on.

**Need help?** Check `DEVELOPER1_README.md` for detailed documentation.
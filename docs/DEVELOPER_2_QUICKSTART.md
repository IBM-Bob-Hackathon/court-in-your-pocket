# Developer 2 - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Prerequisites
- Node.js 18+ installed
- Python 3.10+ installed
- IBM watsonx API credentials (optional for testing)

---

## Step 1: Backend Setup

```bash
# Navigate to backend
cd backend

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env and add your IBM watsonx credentials (optional)
# WATSONX_API_KEY=your_key
# WATSONX_PROJECT_ID=your_project_id

# Start the server
uvicorn main:app --reload
```

✅ Backend running at http://localhost:8000
✅ API docs at http://localhost:8000/docs

---

## Step 2: Frontend Setup

```bash
# Navigate to frontend (in new terminal)
cd frontend

# Install dependencies
npm install

# Create .env file
cp .env.example .env

# Start the dev server
npm run dev
```

✅ Frontend running at http://localhost:5173

---

## Step 3: Test the Chat Interface

1. Open http://localhost:5173 in your browser
2. You should see the chat interface
3. Type a message: "My landlord is not returning my deposit"
4. Bob should respond with a follow-up question
5. Continue the conversation

---

## 📝 Testing Without IBM watsonx

The intake agent has a fallback mode that works without IBM watsonx:
- Uses regex-based fact extraction
- Less intelligent but functional
- Perfect for development and testing

To test with watsonx:
1. Get API credentials from IBM Cloud
2. Add to `backend/.env`
3. Restart backend server

---

## 🧪 Run Tests

```bash
# Backend tests
cd backend
pytest tests/test_chat_api.py -v

# Expected output:
# ✓ test_initial_greeting
# ✓ test_normal_message
# ✓ test_safety_block
# ✓ test_invalid_session
# ✓ test_fact_extraction
# ✓ test_stage_transition
```

---

## 🎯 Test Scenarios

### Scenario 1: Happy Path
```
User: "My landlord is not returning my deposit"
Bob: "Which city are you in?"
User: "Bangalore"
Bob: "How much was the deposit?"
User: "50000"
Bob: "When did you move out?"
User: "2 months ago"
Bob: "What is your landlord's name?"
User: "Mr. Sharma"
Bob: "Thank you! Let me analyze..." → Transitions to analysis
```

### Scenario 2: Voice Input
1. Click microphone button
2. Say: "My landlord is not returning my deposit"
3. Text appears in input field
4. Click Send
5. Bob responds

### Scenario 3: Safety Block
```
User: "How do I hide evidence?"
→ Red safety screen appears
→ Shows emergency contacts
→ Cannot continue
```

---

## 🔍 Verify Implementation

### Frontend Components ✓
- [ ] MessageBubble displays correctly
- [ ] TypingIndicator animates
- [ ] ChipOptions appear and work
- [ ] ProgressTracker shows stage
- [ ] SafetyBlockScreen blocks dangerous content
- [ ] EmergencyPanel shows for out-of-scope
- [ ] Voice input works (Chrome/Edge)

### Backend API ✓
- [ ] POST /api/chat/message returns 200
- [ ] Safety check works
- [ ] Facts extracted from messages
- [ ] Conversation history maintained
- [ ] Stage transitions correctly
- [ ] Session management works

### Integration ✓
- [ ] Frontend calls backend successfully
- [ ] Messages appear in real-time
- [ ] Typing indicator shows during API calls
- [ ] Stage transitions trigger navigation
- [ ] Error handling works

---

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall

# Check for port conflicts
# Kill process on port 8000 if needed
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 18+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install

# Check for port conflicts
# Kill process on port 5173 if needed
```

### Voice input not working
- Only works in Chrome and Edge
- Check microphone permissions
- Try in incognito mode
- Check browser console for errors

### IBM watsonx errors
- Verify API key and project ID in .env
- Check internet connection
- Fallback mode will activate automatically

---

## 📚 Next Steps

1. ✅ Basic setup complete
2. ✅ Test all scenarios
3. ✅ Review code and documentation
4. 🔄 Integrate with Developer 1's session management
5. 🔄 Integrate with Developer 3's legal analysis
6. 🔄 Test end-to-end flow
7. 🚀 Deploy to production

---

## 📞 Need Help?

- Check `DEVELOPER_2_README.md` for detailed documentation
- Check `DEVELOPER_2_IMPLEMENTATION_PLAN.md` for implementation details
- Review code comments in source files
- Test with provided test suite

---

**Status:** ✅ Ready for Development
**Last Updated:** 2026-05-16
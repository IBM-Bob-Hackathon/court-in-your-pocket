# Troubleshooting Guide - Developer 2

## Python Installation Issues

### Issue: "Fatal error in launcher: Unable to create process"

This error occurs when Python paths are misconfigured. Here are solutions:

### Solution 1: Use python -m pip (Recommended)

```bash
cd backend
python -m pip install -r requirements.txt
```

This bypasses the pip launcher and uses Python's module system directly.

### Solution 2: Reinstall Python

1. Download Python 3.10+ from https://www.python.org/downloads/
2. During installation, check "Add Python to PATH"
3. Choose "Install for all users"
4. After installation, verify:
```bash
python --version
python -m pip --version
```

### Solution 3: Use Virtual Environment (Best Practice)

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate it (Windows)
venv\Scripts\activate

# Activate it (Mac/Linux)
source venv/bin/activate

# Install dependencies
python -m pip install -r requirements.txt
```

### Solution 4: Install Packages Individually

If requirements.txt fails, install one by one:

```bash
python -m pip install fastapi==0.104.1
python -m pip install uvicorn[standard]==0.24.0
python -m pip install pydantic==2.5.0
python -m pip install python-dotenv==1.0.0
python -m pip install ibm-watsonx-ai==0.2.6
python -m pip install python-multipart==0.0.6
```

---

## Alternative: Run Without IBM watsonx

The application works without IBM watsonx credentials using fallback mode:

### Minimal Installation

```bash
cd backend

# Install only essential packages
python -m pip install fastapi uvicorn pydantic python-dotenv python-multipart

# Skip ibm-watsonx-ai for now
```

The intake agent will automatically use regex-based extraction instead.

---

## Frontend Installation Issues

### Issue: npm install fails

```bash
cd frontend

# Clear cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Issue: Port 5173 already in use

```bash
# Kill the process (Windows)
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Or use different port
npm run dev -- --port 3000
```

---

## Backend Startup Issues

### Issue: uvicorn command not found

```bash
# Use python -m instead
python -m uvicorn main:app --reload
```

### Issue: Module import errors

Make sure you're in the backend directory:
```bash
cd backend
python -m uvicorn main:app --reload
```

### Issue: Port 8000 already in use

```bash
# Use different port
python -m uvicorn main:app --reload --port 8001

# Update frontend .env
VITE_API_URL=http://localhost:8001
```

---

## Testing Without Full Setup

### Quick Test - Backend Only

```bash
cd backend

# Install minimal dependencies
python -m pip install fastapi uvicorn pydantic python-dotenv

# Start server
python -m uvicorn main:app --reload
```

Visit http://localhost:8000/docs to see API documentation.

### Quick Test - Frontend Only

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev
```

The frontend will show errors when calling API, but you can see the UI.

---

## Common Errors and Fixes

### Error: "Import fastapi could not be resolved"

This is just a VS Code warning. The code will run fine. To fix:

1. Install Python extension for VS Code
2. Select correct Python interpreter (Ctrl+Shift+P → "Python: Select Interpreter")
3. Choose the interpreter where packages are installed

### Error: "CORS policy blocked"

Make sure backend is running and CORS is configured in `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Error: "Session not found"

This happens if backend restarted. Just refresh the frontend page.

---

## Verification Checklist

### Backend Running ✓
- [ ] Navigate to http://localhost:8000
- [ ] Should see: `{"message": "Welcome to Court in Your Pocket API"}`
- [ ] Navigate to http://localhost:8000/docs
- [ ] Should see: FastAPI Swagger documentation

### Frontend Running ✓
- [ ] Navigate to http://localhost:5173
- [ ] Should see: Chat interface
- [ ] Open browser console (F12)
- [ ] Should see no errors (or only API connection errors if backend not running)

### Integration Working ✓
- [ ] Both backend and frontend running
- [ ] Type message in chat
- [ ] Should see Bob's response
- [ ] Check Network tab in browser (F12)
- [ ] Should see POST request to /api/chat/message with 200 status

---

## Still Having Issues?

### Check Python Installation

```bash
# Check Python version
python --version

# Should be 3.10 or higher
# If not, download from python.org
```

### Check Node Installation

```bash
# Check Node version
node --version

# Should be 18 or higher
# If not, download from nodejs.org
```

### Check Directory Structure

Make sure you're in the right directory:

```
court-in-your-pocket/
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   └── ...
└── frontend/
    ├── package.json
    ├── vite.config.js
    └── ...
```

### Get Help

1. Check error messages carefully
2. Search error message online
3. Check Python/Node versions
4. Try virtual environment approach
5. Install packages one by one

---

## Working Configuration (Tested)

### Windows 10/11
- Python 3.10.11
- Node.js 18.17.0
- npm 9.6.7

### Commands that work:
```bash
# Backend
cd backend
python -m venv venv
venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload

# Frontend (new terminal)
cd frontend
npm install
npm run dev
```

---

## Quick Fix Summary

**If pip doesn't work:**
```bash
python -m pip install <package>
```

**If uvicorn doesn't work:**
```bash
python -m uvicorn main:app --reload
```

**If imports fail:**
```bash
# Make sure you're in backend directory
cd backend
python -m uvicorn main:app --reload
```

**If ports conflict:**
```bash
# Backend: use --port 8001
# Frontend: use -- --port 3000
```

---

Last Updated: 2026-05-16
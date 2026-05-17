# Quick Setup Instructions - Developer 1 Frontend

## Prerequisites
- Node.js 18+ installed
- Backend server running on port 8000

## Installation Steps

### 1. Install Dependencies
```bash
cd frontend
npm install
```

Required packages that will be installed:
- `react-router-dom` - For routing
- `zustand` - For state management  
- `tailwindcss` - For styling
- `postcss` - For CSS processing
- `autoprefixer` - For CSS vendor prefixes

### 2. Verify Configuration Files

The following files should already exist:
- `tailwind.config.js` - Tailwind theme configuration
- `postcss.config.js` - PostCSS configuration
- `.env` - Environment variables (API URL)

### 3. Start Development Server
```bash
npm run dev
```

The app will run on `http://localhost:5173`

### 4. Start Backend Server
In a separate terminal:
```bash
cd backend
python -m uvicorn main:app --reload
```

Backend will run on `http://localhost:8000`

## Testing the Implementation

1. Open `http://localhost:5173` in your browser
2. You will be automatically redirected to `http://localhost:5173/welcome`
3. You should see the Landing screen with:
   - Language toggle (EN/HI) in top-right
   - "Court in Your Pocket" title
   - State selector dropdown
   - "Get Started" button
   - Disclaimer text

3. Test the flow:
   - Toggle language - text should change
   - Select a state (Karnataka, Maharashtra, or Delhi)
   - Click "Get Started"
   - Should navigate to Chat screen (placeholder)

4. Check browser DevTools:
   - Network tab: Should see POST to `/api/session/start`
   - Console: Should see no errors
   - Application > Local Storage: Should see `court-in-pocket-storage` with session data

## Troubleshooting

### Dependencies not installing
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Backend connection fails
- Verify backend is running: `curl http://localhost:8000/health`
- Check `.env` file has correct URL: `VITE_API_BASE_URL=http://localhost:8000`
- Check for CORS errors in browser console

### Styles not working
```bash
# Restart dev server
# Press Ctrl+C to stop, then:
npm run dev
```

### Port 5173 already in use
```bash
# Kill the process using port 5173
# Windows:
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Mac/Linux:
lsof -ti:5173 | xargs kill -9
```

## File Structure Created

```
frontend/
├── src/
│   ├── components/
│   │   └── ErrorBoundary.jsx
│   ├── screens/
│   │   ├── Landing.jsx
│   │   ├── Chat.jsx (placeholder)
│   │   ├── Rights.jsx (placeholder)
│   │   └── ActionPlan.jsx (placeholder)
│   ├── store/
│   │   └── useAppStore.js
│   ├── App.jsx
│   ├── main.jsx
│   └── index.css
├── tailwind.config.js
├── postcss.config.js
├── .env
└── .env.example
```

## Next Steps

1. ✅ Frontend structure is complete
2. ✅ Landing screen is functional
3. ✅ Routing is set up
4. ✅ State management is configured
5. ⏳ Waiting for Developer 2 to implement Chat screen
6. ⏳ Waiting for Developer 3 to implement Rights screen
7. ⏳ Waiting for Developer 4 to implement Action Plan screen

## Integration Notes

### For Other Developers

**Accessing Global State:**
```javascript
import useAppStore from '../store/useAppStore';

function YourComponent() {
  const { sessionId, language, state, stage } = useAppStore();
  const { setStage } = useAppStore();
  
  // Use the state...
}
```

**Available State:**
- `sessionId` - UUID from backend
- `language` - 'en' or 'hi'
- `state` - 'KA', 'MH', or 'DL'
- `stage` - Current stage of the flow

**Available Actions:**
- `setSessionId(id)`
- `setLanguage(lang)`
- `setState(state)`
- `setStage(stage)`
- `initializeSession(id, lang, state)`
- `resetSession()`

**Protected Routes:**
All routes except `/welcome` require a valid `sessionId`. If user tries to access a protected route without a session, they'll be redirected to `/welcome`.

**Root Path:**
The root path `/` automatically redirects to `/welcome` for a cleaner URL structure.

## API Endpoint Used

### POST /api/session/start
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

## Support

For issues or questions:
1. Check the main README_DEVELOPER1.md for detailed documentation
2. Verify backend is running and accessible
3. Check browser console for errors
4. Verify all dependencies are installed
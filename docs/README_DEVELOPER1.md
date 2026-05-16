# Developer 1 - Frontend Implementation

## Overview
This document describes the Developer 1 frontend implementation for the "Court in Your Pocket" project, including the Landing/Onboarding screen, App Shell, and global state management.

## What's Implemented

### 1. App Shell & Routing
- **React Router Setup** ([`App.jsx`](src/App.jsx))
  - Route definitions: `/` → `/welcome` → `/chat` → `/rights` → `/action`
  - Root path `/` automatically redirects to `/welcome`
  - Protected routes that require a valid session
  - Automatic redirect to welcome page if no session exists
  
### 2. Global State Management
- **Zustand Store** ([`store/useAppStore.js`](src/store/useAppStore.js))
  - Manages: `sessionId`, `language`, `state`, `stage`
  - Persists to localStorage automatically
  - Actions: `setSessionId`, `setLanguage`, `setState`, `setStage`, `initializeSession`, `resetSession`

### 3. Error Boundary
- **Global Error Handler** ([`components/ErrorBoundary.jsx`](src/components/ErrorBoundary.jsx))
  - Catches React errors throughout the app
  - Displays user-friendly error screen
  - Shows error details in development
  - Provides refresh button

### 4. Landing/Onboarding Screen
- **Landing Component** ([`screens/Landing.jsx`](src/screens/Landing.jsx))
  - "Get Started" CTA button
  - State selector dropdown (KA / MH / DL)
  - Language toggle EN/HI (persists in localStorage)
  - Disclaimer: "Not a law firm. A legal compass."
  - Calls `POST /api/session/start` to initialize session
  - Navigates to Chat screen on successful start

### 5. Tailwind Theme
- **Custom Theme** ([`tailwind.config.js`](tailwind.config.js))
  - Dark navy color palette (navy-50 to navy-950)
  - Gold accent colors (gold-50 to gold-900)
  - Custom fonts: Inter (sans), Poppins (heading)
  - Mobile-first responsive design

### 6. Placeholder Screens
Created placeholder screens for other developers:
- [`screens/Chat.jsx`](src/screens/Chat.jsx) - Developer 2
- [`screens/Rights.jsx`](src/screens/Rights.jsx) - Developer 3
- [`screens/ActionPlan.jsx`](src/screens/ActionPlan.jsx) - Developer 4

## Installation & Setup

### Prerequisites
- Node.js 18+ and npm installed
- Backend server running on `http://localhost:8000`

### Step 1: Install Dependencies
```bash
cd frontend
npm install
```

This will install:
- `react-router-dom` - Routing
- `zustand` - State management
- `tailwindcss`, `postcss`, `autoprefixer` - Styling

### Step 2: Configure Environment
The `.env` file is already created with:
```
VITE_API_BASE_URL=http://localhost:8000
```

If your backend runs on a different port, update this value.

### Step 3: Run Development Server
```bash
npm run dev
```

The app will be available at `http://localhost:5173`

## File Structure

```
frontend/
├── src/
│   ├── components/
│   │   └── ErrorBoundary.jsx       # Global error boundary
│   ├── screens/
│   │   ├── Landing.jsx             # Landing/Onboarding screen
│   │   ├── Chat.jsx                # Placeholder for Developer 2
│   │   ├── Rights.jsx              # Placeholder for Developer 3
│   │   └── ActionPlan.jsx          # Placeholder for Developer 4
│   ├── store/
│   │   └── useAppStore.js          # Zustand global state
│   ├── App.jsx                     # Main app with routing
│   ├── main.jsx                    # Entry point
│   └── index.css                   # Tailwind imports
├── tailwind.config.js              # Tailwind theme configuration
├── postcss.config.js               # PostCSS configuration
├── .env                            # Environment variables
└── .env.example                    # Environment template
```

## API Integration

### POST /api/session/start
The Landing screen calls this endpoint when the user clicks "Get Started":

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

The session ID is stored in Zustand and localStorage, then used for all subsequent API calls.

## State Management

### Global State Structure
```javascript
{
  sessionId: null,           // UUID from backend
  language: 'en',            // 'en' or 'hi'
  state: null,               // 'KA', 'MH', or 'DL'
  stage: 'landing'           // 'landing' | 'intake' | 'analysis' | 'document' | 'complete'
}
```

### Usage Example
```javascript
import useAppStore from './store/useAppStore';

function MyComponent() {
  const { sessionId, language, setLanguage } = useAppStore();
  
  const toggleLanguage = () => {
    setLanguage(language === 'en' ? 'hi' : 'en');
  };
  
  return <div>{sessionId ? 'Logged in' : 'Not logged in'}</div>;
}
```

## Routing

### Route Protection
All routes except `/` require a valid `sessionId`:
- If user tries to access `/chat`, `/rights`, or `/action` without a session, they're redirected to `/`
- After successful session creation on Landing, user is navigated to `/chat`

### Route Definitions
- `/` - Automatically redirects to `/welcome`
- `/welcome` - Landing/Onboarding (public)
- `/chat` - Chat Interface (protected)
- `/rights` - Your Rights (protected)
- `/action` - Action Plan (protected)
- `*` - Catch-all redirects to `/welcome`

## Styling

### Tailwind Classes
The theme uses:
- **Background**: `bg-navy-950` (dark navy)
- **Cards**: `bg-navy-900` with `border-navy-800`
- **Text**: `text-white`, `text-gray-400`, `text-gray-300`
- **Accent**: `bg-gold-500`, `text-gold-500`
- **Buttons**: `bg-gold-500 hover:bg-gold-600`

### Responsive Design
All components are mobile-first with responsive breakpoints:
- Base: Mobile (< 640px)
- sm: 640px+
- md: 768px+
- lg: 1024px+

## Testing Checklist

- [ ] Landing page loads correctly
- [ ] Language toggle switches between EN/HI
- [ ] State selector shows all 3 states
- [ ] Error message appears if "Get Started" clicked without selecting state
- [ ] Session creation API call succeeds
- [ ] After session creation, user is redirected to `/chat`
- [ ] Session data persists in localStorage
- [ ] Protected routes redirect to `/` if no session
- [ ] Error boundary catches and displays errors
- [ ] Responsive design works on mobile and desktop

## Integration Points

### For Developer 2 (Chat Interface)
- Access session data: `const { sessionId, language, state } = useAppStore()`
- Update stage: `setStage('analysis')` when moving to next phase
- Session is already initialized when user reaches `/chat`

### For Developer 3 (Rights Screen)
- Access session data from store
- Navigate to `/action` when user clicks "Build My Action Plan"

### For Developer 4 (Action Plan)
- Access session data from store
- Can reset session with `resetSession()` if needed

## Notes

- The backend must be running for the Landing screen to work
- Session expires after 30 minutes (handled by backend)
- Language preference persists across sessions via localStorage
- All API calls should include error handling
- The app uses dark theme by default (navy background)

## Troubleshooting

### "npm is not recognized"
Make sure Node.js is installed and added to PATH.

### API calls fail
1. Check backend is running on `http://localhost:8000`
2. Verify `.env` has correct `VITE_API_BASE_URL`
3. Check browser console for CORS errors

### Styles not applying
1. Make sure Tailwind is installed: `npm install tailwindcss postcss autoprefixer`
2. Restart dev server after installing Tailwind
3. Check `index.css` has Tailwind directives

### State not persisting
- Check browser localStorage in DevTools
- Look for key: `court-in-pocket-storage`
- Clear localStorage if corrupted: `localStorage.clear()`

## Next Steps

1. Install dependencies: `npm install`
2. Start backend server
3. Start frontend: `npm run dev`
4. Test Landing screen flow
5. Coordinate with Developer 2 for Chat screen integration
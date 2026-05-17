# Data Flow - Welcome Screen to Other Screens

## Overview
This document explains how user inputs (state and language) from the Welcome screen are captured, sent to the backend, and made available to other screens.

## User Input Collection (Welcome Screen)

### Inputs Collected
1. **State** - User selects from dropdown:
   - Karnataka (KA)
   - Maharashtra (MH)
   - Delhi (DL)

2. **Language** - User toggles between:
   - English (en)
   - Hindi (hi)
   - Or any other languages from the dropdown

## API Call Flow

### Step 1: User Clicks "Get Started"
When the user clicks the "Get Started" button on [`/welcome`](src/screens/Landing.jsx:24-62):

```javascript
const handleGetStarted = async () => {
  // Validate state is selected
  if (!selectedState) {
    setError('Please select your state');
    return;
  }

  // Call backend API
  const response = await fetch(`${API_BASE_URL}/api/session/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      language,        // 'en' or 'hi'
      state: selectedState,  // 'KA', 'MH', or 'DL'
    }),
  });
}
```

### Step 2: Backend Creates Session
The backend endpoint `POST /api/session/start` receives:

**Request Body:**
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

### Step 3: Store Session Data
After receiving the session ID, the data is stored in Zustand global state ([`store/useAppStore.js`](src/store/useAppStore.js:27-32)):

```javascript
initializeSession(data.sessionId, language, selectedState);
```

This stores:
- `sessionId` - UUID from backend
- `language` - User's selected language
- `state` - User's selected state
- `stage` - Set to 'intake' (next phase)

### Step 4: Persist to localStorage
Zustand automatically persists this data to browser localStorage with key `court-in-pocket-storage`.

This means the data survives:
- Page refreshes
- Browser restarts
- Navigation between pages

## Accessing Data in Other Screens

### For Developer 2 (Chat Screen)
```javascript
import useAppStore from '../store/useAppStore';

function Chat() {
  const { sessionId, language, state, stage } = useAppStore();
  
  // Use the data
  console.log('Session ID:', sessionId);
  console.log('User Language:', language);  // 'en' or 'hi'
  console.log('User State:', state);        // 'KA', 'MH', or 'DL'
  console.log('Current Stage:', stage);     // 'intake'
  
  // Make API calls with session data
  const sendMessage = async (message) => {
    const response = await fetch('/api/chat/message', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId,
        message,
        // Backend already has language and state from session
      }),
    });
  };
}
```

### For Developer 3 (Rights Screen)
```javascript
import useAppStore from '../store/useAppStore';

function Rights() {
  const { sessionId, language, state } = useAppStore();
  
  // Display content in user's language
  const content = language === 'en' ? englishContent : hindiContent;
  
  // Show state-specific information
  const stateInfo = getStateInfo(state);
  
  return (
    <div>
      <h1>{content.title}</h1>
      <p>{stateInfo.description}</p>
    </div>
  );
}
```

### For Developer 4 (Action Plan Screen)
```javascript
import useAppStore from '../store/useAppStore';

function ActionPlan() {
  const { sessionId, language, state } = useAppStore();
  
  // Generate action plan based on state
  const generatePlan = async () => {
    const response = await fetch('/api/action-plan/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        sessionId,
        option: selectedOption,
      }),
    });
  };
}
```

## Complete Data Flow Diagram

```
┌─────────────────────────────────────────────────────────┐
│ 1. Welcome Screen (/welcome)                            │
│    User selects: State (KA/MH/DL) + Language (EN/HI)   │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 2. POST /api/session/start                              │
│    Body: { language: "en", state: "KA" }               │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 3. Backend Creates Session                              │
│    Returns: { sessionId: "uuid" }                       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 4. Zustand Store (Global State)                         │
│    sessionId: "uuid"                                    │
│    language: "en"                                       │
│    state: "KA"                                          │
│    stage: "intake"                                      │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 5. localStorage (Persistence)                           │
│    Key: "court-in-pocket-storage"                       │
│    Survives page refresh & browser restart              │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│ 6. Navigate to /chat                                    │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
        ▼            ▼            ▼
   ┌────────┐  ┌─────────┐  ┌──────────┐
   │  Chat  │  │ Rights  │  │  Action  │
   │ Screen │  │ Screen  │  │   Plan   │
   └────────┘  └─────────┘  └──────────┘
        │            │            │
        └────────────┴────────────┘
                     │
                     ▼
        All screens access same data via:
        useAppStore() hook
```

## Key Points

### 1. Single Source of Truth
All session data is stored in one place: Zustand store. Any screen can access it using the `useAppStore()` hook.

### 2. Automatic Persistence
Data is automatically saved to localStorage, so users don't lose their session if they:
- Refresh the page
- Close and reopen the browser
- Navigate between screens

### 3. Backend Session Management
The backend maintains its own session store using the `sessionId`. When other screens make API calls, they only need to send the `sessionId` - the backend already knows the language and state.

### 4. Protected Routes
All screens except `/welcome` require a valid `sessionId`. If a user tries to access them without a session, they're redirected back to `/welcome`.

### 5. Language Preference
The language selection persists across the entire session and is used by all screens to display content in the user's preferred language.

## Example: Complete User Journey

```
1. User visits http://localhost:5173
   → Redirected to http://localhost:5173/welcome

2. User selects:
   - State: Karnataka (KA)
   - Language: English (EN)
   - Clicks "Get Started"

3. Frontend calls:
   POST /api/session/start
   Body: { language: "en", state: "KA" }

4. Backend responds:
   { sessionId: "abc-123-xyz" }

5. Frontend stores in Zustand:
   {
     sessionId: "abc-123-xyz",
     language: "en",
     state: "KA",
     stage: "intake"
   }

6. User navigates to /chat
   Chat screen accesses: useAppStore()
   Gets: sessionId, language, state

7. User navigates to /rights
   Rights screen accesses: useAppStore()
   Gets: same sessionId, language, state

8. User navigates to /action
   Action Plan screen accesses: useAppStore()
   Gets: same sessionId, language, state

9. User refreshes page
   Data persists from localStorage
   Session continues seamlessly
```

## For Backend Developers

When you receive API calls from other screens, you'll get the `sessionId` in the request body. You can then:

1. Look up the session in your session store
2. Retrieve the language and state from the session
3. Use that information to provide appropriate responses

Example backend session lookup:
```python
# In your API endpoint
session = session_store.get_session(sessionId)
language = session['language']  # 'en' or 'hi'
state = session['state']        # 'KA', 'MH', or 'DL'

# Use this data to customize response
if language == 'hi':
    response = hindi_response
else:
    response = english_response
```

## Troubleshooting

### Data not persisting
- Check browser localStorage in DevTools
- Look for key: `court-in-pocket-storage`
- If corrupted, clear it: `localStorage.clear()`

### Session not found
- Verify backend is running
- Check that `/api/session/start` returns valid sessionId
- Ensure sessionId is being stored in Zustand

### Wrong language/state
- Check that user selection is being captured correctly
- Verify the values being sent to backend
- Confirm Zustand store is updating properly
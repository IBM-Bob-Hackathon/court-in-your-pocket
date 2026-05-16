# RightsScreen Component

## Overview
The **RightsScreen** is Screen 2 in the "Court in Your Pocket" app flow. It displays the user's legal rights based on their situation, retrieved from the backend legal analysis API.

## Features Implemented

### 1. **Data Fetching**
- On mount, calls `POST /api/legal/analyze` with `{sessionId}` from React Context
- Shows loading spinner while fetching
- Handles errors gracefully with error screen

### 2. **Collapsible Situation Summary**
- Card at the top that can be expanded/collapsed
- Provides context about what Bob understood from the conversation

### 3. **Rights Display Cards**
Each right includes:
- **Law name** (e.g., "Model Tenancy Act 2021") in yellow
- **Section** (e.g., "Section 11") in grey, smaller text
- **Plain English explanation** in bold white text
- **Confidence badge**: 5 dots (●●●●●) - filled dots are green, empty are grey
- **Last verified badge**: 
  - Green: < 3 months old ("Recently verified")
  - Amber: 3-6 months old ("Verify for recent changes")
  - Red: > 6 months old ("Confirm with official source")
- **Expandable section** showing:
  - Exact quote from the law (in italics with yellow border)
  - Link to official source URL (opens in new tab)

### 4. **Deadline Warning Banner**
- Amber warning banner at top if `deadline` exists
- Shows: "You have ~X days to act"
- Includes warning icon

### 5. **Option Selection**
- Three option buttons (A, B, C) with labels from API
- Selected option has yellow border and yellow background tint
- Radio-style selection with checkmark indicator

### 6. **Action Plan Button**
- Fixed at bottom of screen
- Disabled (grey) until an option is selected
- Enabled (yellow) after selection
- On click, navigates to `/action` with selected option in React Router state

### 7. **Overall Confidence Score**
- Shows aggregate confidence score with 5-dot visualization
- Displays numerical score (e.g., "4/5")

## Tech Stack
- **React** with hooks (useState, useEffect)
- **React Router** for navigation
- **Tailwind CSS** for all styling
- **React Context** for session management

## Props & Context
- Uses `useAppContext()` to get `sessionId`
- No props required - all data fetched internally

## API Contract

### Request
```json
POST /api/legal/analyze
{
  "sessionId": "uuid-string"
}
```

### Response
```json
{
  "rights": [
    {
      "law_name": "Model Tenancy Act 2021",
      "section": "Section 11",
      "plain_english": "Your landlord must return your security deposit within 1 month of vacating.",
      "exact_quote": "The landlord shall refund the security deposit...",
      "confidence": 4,
      "last_verified": "2026-05-01",
      "source_url": "https://indiacode.nic.in/..."
    }
  ],
  "confidence": 4,
  "deadline": 18,
  "options": [
    {"id": "A", "label": "Send demand letter"},
    {"id": "B", "label": "File complaint"},
    {"id": "C", "label": "Free legal aid"}
  ]
}
```

## Styling
- **Background**: Dark navy (`bg-slate-900`)
- **Accent color**: Gold/yellow (`text-yellow-500`, `bg-yellow-500`)
- **Cards**: Slate grey (`bg-slate-800`) with borders
- **Mobile-first**: Responsive design with max-width container
- **Fixed bottom button**: Stays at bottom on scroll

## Navigation Flow
```
Chat Screen → RightsScreen → Action Plan Screen
                    ↓
            (passes selectedOption via state)
```

## Installation

### 1. Install Dependencies
```bash
cd frontend
npm install react-router-dom
```

### 2. Update main.jsx
Wrap your app with AppProvider and BrowserRouter:

```jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { BrowserRouter } from 'react-router-dom'
import { AppProvider } from './context/AppContext'
import './index.css'
import App from './App.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <BrowserRouter>
      <AppProvider>
        <App />
      </AppProvider>
    </BrowserRouter>
  </StrictMode>,
)
```

### 3. Update App.jsx
Set up routes:

```jsx
import { Routes, Route } from 'react-router-dom'
import RightsScreen from './screens/RightsScreen'
// Import other screens...

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingScreen />} />
      <Route path="/chat" element={<ChatScreen />} />
      <Route path="/rights" element={<RightsScreen />} />
      <Route path="/action" element={<ActionScreen />} />
    </Routes>
  )
}

export default App
```

## Usage Example

```jsx
import RightsScreen from './screens/RightsScreen'

// In your router setup
<Route path="/rights" element={<RightsScreen />} />
```

The component will automatically:
1. Fetch session data from context
2. Call the API
3. Display results
4. Handle user interaction
5. Navigate to next screen

## Error Handling
- No session: Shows error message with "Go Back" button
- API failure: Shows error card with error message
- Loading state: Shows spinner with "Analyzing your legal situation..." message

## Accessibility
- Semantic HTML structure
- Keyboard navigation support
- ARIA labels on interactive elements
- Color contrast meets WCAG standards
- Focus states on all interactive elements

## Browser Compatibility
- Modern browsers (Chrome, Firefox, Safari, Edge)
- Requires JavaScript enabled
- Responsive design works on mobile and desktop

## Developer Notes
- All styling uses Tailwind utility classes
- No external component libraries
- State management via React hooks
- API endpoint configurable via environment variables (if needed)
- Component is fully self-contained and reusable
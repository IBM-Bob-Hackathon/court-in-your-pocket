import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ErrorBoundary from './screens/ErrorBoundary';
import Landing from './screens/LandingScreen';
import Chat from './screens/ChatScreen';
import Rights from './screens/RightsScreen';
import ActionPlan from './screens/ActionPlanScreen';
import useAppStore from './store/useAppStore';

function App() {
  const { sessionId } = useAppStore();

  return (
    <ErrorBoundary>
      <Router>
        <Routes>
          {/* Root redirects to welcome */}
          <Route path="/" element={<Navigate to="/welcome" replace />} />
          
          {/* Landing/Onboarding Screen */}
          <Route path="/welcome" element={<Landing />} />
          
          {/* Chat Interface - Protected route */}
          <Route
            path="/chat"
            element={sessionId ? <Chat /> : <Navigate to="/welcome" replace />}
          />
          
          {/* Rights Screen - Protected route */}
          <Route
            path="/rights"
            element={sessionId ? <Rights /> : <Navigate to="/welcome" replace />}
          />
          
          {/* Action Plan Screen - Protected route */}
          <Route
            path="/action"
            element={sessionId ? <ActionPlan /> : <Navigate to="/welcome" replace />}
          />
          
          {/* Catch all - redirect to welcome */}
          <Route path="*" element={<Navigate to="/welcome" replace />} />
        </Routes>
      </Router>
    </ErrorBoundary>
  );
}

export default App;

// Made with Bob

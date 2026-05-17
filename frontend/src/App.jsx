import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import ChatScreen from './screens/ChatScreen';
import OnboardingScreen from './screens/LandingScreen';
import './App.css';

const RightsPlaceholder = () => {
  return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center gap-6">
      <h1 className="text-2xl font-bold text-amber-400">Rights Screen</h1>
      <p className="text-slate-400 text-sm">Developer 3 will implement this screen.</p>
      <button onClick={() => window.history.back()} className="mt-4 px-6 py-2 bg-amber-500 hover:bg-amber-600 text-slate-900 font-semibold rounded-xl transition-colors">← Go Back</button>
    </div>
  );
};

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<OnboardingScreen />} />
        <Route path="/chat" element={<ChatScreen />} />
        <Route path="/rights" element={<RightsPlaceholder />} />
      </Routes>
    </Router>
  );
}

export default App;

// Made with Bob

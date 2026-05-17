import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import useAppStore from '../store/useAppStore';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const Landing = () => {
  const navigate = useNavigate();
  const { language, setLanguage, initializeSession, resetSession, sessionId } = useAppStore();
  const [selectedState, setSelectedState] = useState('');
  const [selectedLanguage, setSelectedLanguage] = useState('en');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Clear session when landing page is mounted
  useEffect(() => {
  // Capture sessionId at the time landing page loads
  // not reactive to future changes
  const sessionToDelete = sessionId;
  
  const clearSession = async () => {
    if (sessionToDelete) {
      try {
        await fetch(`${API_BASE_URL}/api/session/${sessionToDelete}`, {
          method: 'DELETE',
        });
      } catch (err) {
        console.error('Error deleting session:', err);
      }
    }
    resetSession();
  };

  clearSession();
}, []); // ← empty deps, runs once on mount, but uses sessionId from closure

  const states = [
    { code: 'KA', name: 'Karnataka' },
    { code: 'MH', name: 'Maharashtra' },
    { code: 'DL', name: 'Delhi' },
    { code: 'UP', name: 'Uttar Pradesh' },
  ];

  const languages = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'हिंदी (Hindi)' },
    { code: 'ta', name: 'தமிழ் (Tamil)' },
    { code: 'te', name: 'తెలుగు (Telugu)' },
    { code: 'kn', name: 'ಕನ್ನಡ (Kannada)' },
    { code: 'mr', name: 'मराठी (Marathi)' },
    { code: 'bn', name: 'বাংলা (Bengali)' },
    { code: 'gu', name: 'ગુજરાતી (Gujarati)' },
  ];

  const handleGetStarted = async () => {
    if (!selectedState) {
      setError('Please select your state');
      return;
    }

    if (!selectedLanguage) {
      setError('Please select your language');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE_URL}/api/session/start`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          language: selectedLanguage,
          state: selectedState,
        }),
      });

      if (!response.ok) {
        // Provide specific error messages based on status code
        if (response.status >= 500) {
          throw new Error('Server error. Please try again later.');
        } else if (response.status === 400) {
          throw new Error('Invalid state or language selection.');
        } else if (!navigator.onLine) {
          throw new Error('No internet connection. Please check your network.');
        } else {
          throw new Error('Failed to start session. Please try again.');
        }
      }

      const data = await response.json();
      
      // Update language in store and initialize session
      setLanguage(selectedLanguage);
      initializeSession(data.sessionId, selectedLanguage, selectedState);
      
      // Navigate to chat
      navigate('/chat');
    } catch (err) {
      console.error('Error starting session:', err);
      // Use the specific error message from the catch block
      setError(err.message || 'Failed to start session. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-navy-950 via-navy-900 to-navy-950 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        {/* Main Content */}
        <div className="bg-navy-900 rounded-2xl shadow-2xl p-8 border border-navy-800">
          {/* Logo/Icon */}
          <div className="flex items-center justify-center w-20 h-20 bg-gold-500/10 rounded-full mx-auto mb-6">
            <svg
              className="w-10 h-10 text-gold-500"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 6l3 1m0 0l-3 9a5.002 5.002 0 006.001 0M6 7l3 9M6 7l6-2m6 2l3-1m-3 1l-3 9a5.002 5.002 0 006.001 0M18 7l3 9m-3-9l-6-2m0-2v2m0 16V5m0 16H9m3 0h3"
              />
            </svg>
          </div>

          {/* Title */}
          <h1 className="text-3xl font-heading font-bold text-white text-center mb-2">
            Court in Your Pocket
          </h1>

          {/* Subtitle */}
          <p className="text-gray-400 text-center mb-8">
            Your free AI-powered legal companion
          </p>

          {/* Language Selector */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Select Your Language
            </label>
            <select
              value={selectedLanguage}
              onChange={(e) => {
                setSelectedLanguage(e.target.value);
                setError(null);
              }}
              className="w-full px-4 py-3 bg-navy-800 border border-navy-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-gold-500 focus:border-transparent"
            >
              <option value="">Choose a language...</option>
              {languages.map((lang) => (
                <option key={lang.code} value={lang.code}>
                  {lang.name}
                </option>
              ))}
            </select>
          </div>

          {/* State Selector */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-300 mb-2">
              Select Your State
            </label>
            <select
              value={selectedState}
              onChange={(e) => {
                setSelectedState(e.target.value);
                setError(null);
              }}
              className="w-full px-4 py-3 bg-navy-800 border border-navy-700 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-gold-500 focus:border-transparent"
            >
              <option value="">Choose a state...</option>
              {states.map((state) => (
                <option key={state.code} value={state.code}>
                  {state.name}
                </option>
              ))}
            </select>
          </div>

          {/* Error Message */}
          {error && (
            <div className="mb-6 p-3 bg-red-500/10 border border-red-500/50 rounded-lg text-red-400 text-sm">
              {error}
            </div>
          )}

          {/* Get Started Button */}
          <button
            onClick={handleGetStarted}
            disabled={isLoading || !selectedState || !selectedLanguage}
            className="w-full bg-gold-500 hover:bg-gold-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-navy-950 font-semibold py-4 px-6 rounded-lg transition-colors text-lg"
          >
            {isLoading ? 'Starting...' : 'Get Started'}
          </button>

          {/* Disclaimer */}
          <p className="text-xs text-gray-500 text-center mt-6 italic">
            Not a law firm. A legal compass.
          </p>
        </div>

        {/* Additional Info */}
        <div className="mt-6 text-center">
          <p className="text-sm text-gray-500">
            Free legal guidance powered by IBM watsonx
          </p>
        </div>
      </div>
    </div>
  );
};

export default Landing;

// Made with Bob

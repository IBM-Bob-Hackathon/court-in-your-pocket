import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import chatAPI from '../services/api';

/**
 * Screen 0 — Language & State selection.
 * Developer 1 will replace this UI with the final design.
 * This screen is responsible for:
 *  1. Collecting language + state from the user
 *  2. Calling the backend to create a session
 *  3. Storing sessionId / language / state in localStorage
 *  4. Navigating to /chat
 */
const OnboardingScreen = () => {
  const navigate = useNavigate();
  const [language, setLanguage] = useState('en');
  const [state, setState] = useState('KA');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleStart = async () => {
    setLoading(true);
    setError(null);
    try {
      const sessionData = await chatAPI.createSession(language, state);
      localStorage.setItem('sessionId', sessionData.sessionId);
      localStorage.setItem('language', sessionData.language || language);
      localStorage.setItem('state', sessionData.state || state);
      navigate('/chat', { replace: true });
    } catch (err) {
      console.error('Failed to create session:', err);
      setError('Unable to connect to the server. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-slate-900 flex flex-col items-center justify-center gap-8 px-4">
      {/* ── Developer 1: replace everything below this line with the real UI ── */}
      <h1 className="text-3xl font-bold text-amber-400">Court in Your Pocket</h1>
      <p className="text-slate-400 text-center max-w-sm">
        Select your preferred language and state to get started.
      </p>

      <div className="flex flex-col gap-4 w-full max-w-xs">
        <div className="flex flex-col gap-1">
          <label className="text-slate-300 text-sm font-medium">Language</label>
          <select
            value={language}
            onChange={e => setLanguage(e.target.value)}
            className="bg-slate-800 text-white border border-slate-600 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-amber-400"
          >
            <option value="en">English</option>
            <option value="hi">हिन्दी</option>
          </select>
        </div>

        <div className="flex flex-col gap-1">
          <label className="text-slate-300 text-sm font-medium">State</label>
          <select
            value={state}
            onChange={e => setState(e.target.value)}
            className="bg-slate-800 text-white border border-slate-600 rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-amber-400"
          >
            <option value="KA">Karnataka</option>
            <option value="MH">Maharashtra</option>
            <option value="DL">Delhi</option>
          </select>
        </div>

        {error && (
          <p className="text-red-400 text-sm text-center">{error}</p>
        )}

        <button
          onClick={handleStart}
          disabled={loading}
          className="bg-amber-500 hover:bg-amber-600 disabled:opacity-50 text-slate-900 font-bold py-3 rounded-xl transition-colors"
        >
          {loading ? 'Starting...' : 'Start'}
        </button>
      </div>
      {/* ── Developer 1: replace everything above this line with the real UI ── */}
    </div>
  );
};

export default OnboardingScreen;

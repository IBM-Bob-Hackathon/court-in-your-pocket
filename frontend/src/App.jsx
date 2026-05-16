import { Routes, Route, useNavigate } from 'react-router-dom'
import RightsScreen from './screens/RightsScreen'
import './App.css'

function LandingPage() {
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-slate-900 flex items-center justify-center p-4">
      <div className="text-center">
        <h1 className="text-4xl md:text-5xl font-bold text-yellow-500 mb-4">
          Court in Your Pocket
        </h1>
        <p className="text-gray-400 text-lg mb-8">
          Your legal rights, simplified
        </p>
        <button
          onClick={() => navigate('/rights')}
          className="bg-yellow-500 hover:bg-yellow-600 text-slate-900 font-semibold px-8 py-4 rounded-lg transition-colors text-lg"
        >
          Get Started
        </button>
      </div>
    </div>
  )
}

function App() {
  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route path="/rights" element={<RightsScreen />} />
    </Routes>
  )
}

export default App

// Made with Bob

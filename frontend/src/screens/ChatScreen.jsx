import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import MessageBubble from '../components/MessageBubble';
import TypingIndicator from '../components/TypingIndicator';
import ChipOptions from '../components/ChipOptions';
import ProgressTracker from '../components/ProgressTracker';
import SafetyBlockScreen from '../components/SafetyBlockScreen';
import EmergencyPanel from '../components/EmergencyPanel';
import chatAPI from '../services/api';

const ChatScreen = () => {
  const navigate = useNavigate();
  const messagesEndRef = useRef(null);
  
  const [sessionId, setSessionId] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [chips, setChips] = useState([]);
  const [currentStage, setCurrentStage] = useState('intake');
  const [showSafetyBlock, setShowSafetyBlock] = useState(false);
  const [showEmergencyPanel, setShowEmergencyPanel] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [language, setLanguage] = useState('en');

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Get sessionId from localStorage on mount
  useEffect(() => {
    let storedSessionId = localStorage.getItem('sessionId');
    const storedLanguage = localStorage.getItem('language') || 'en';
    
    // Create a mock session if none exists
    if (!storedSessionId) {
      storedSessionId = 'mock-session-' + Date.now();
      localStorage.setItem('sessionId', storedSessionId);
      localStorage.setItem('language', 'en');
      localStorage.setItem('state', 'KA');
    }
    
    setSessionId(storedSessionId);
    setLanguage(storedLanguage);
    
    // Send initial greeting
    sendInitialGreeting(storedSessionId);
  }, []);

  const sendInitialGreeting = async (sid) => {
    setIsTyping(true);
    try {
      const response = await chatAPI.sendMessage(sid, '__INIT__');
      setMessages([{
        sender: 'bob',
        message: response.reply,
        timestamp: new Date(),
      }]);
      setChips(response.chips || []);
      setCurrentStage(response.stage);
    } catch (error) {
      console.error('Failed to get initial greeting:', error);
      setMessages([{
        sender: 'bob',
        message: 'Namaste! What legal issue are you facing today?',
        timestamp: new Date(),
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleSendMessage = async (text) => {
    if (!text.trim() || !sessionId) return;

    // Add user message to UI
    const userMessage = {
      sender: 'user',
      message: text,
      timestamp: new Date(),
    };
    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setChips([]);

    // Show typing indicator
    setIsTyping(true);

    try {
      const response = await chatAPI.sendMessage(sessionId, text);

      // Check for safety block
      if (response.safetyBlocked) {
        setShowSafetyBlock(true);
        setIsTyping(false);
        return;
      }

      // Check for out of scope
      if (response.stage === 'out_of_scope') {
        setShowEmergencyPanel(true);
      }

      // Add Bob's response
      const bobMessage = {
        sender: 'bob',
        message: response.reply,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, bobMessage]);
      setChips(response.chips || []);
      setCurrentStage(response.stage);

      // Check for stage transition to analysis
      if (response.stage === 'analysis') {
        // Wait a moment, then navigate to rights screen
        setTimeout(() => {
          navigate('/rights');
        }, 2000);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
      // Show error message
      const errorMessage = {
        sender: 'bob',
        message: 'Sorry, I encountered an error. Please try again.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleChipSelect = (chip) => {
    handleSendMessage(chip);
  };

  const startVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Voice input not supported in this browser. Please use Chrome or Edge.');
      return;
    }

    const recognition = new window.webkitSpeechRecognition();
    recognition.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
    recognition.continuous = false;
    recognition.interimResults = false;

    recognition.onstart = () => setIsListening(true);
    recognition.onend = () => setIsListening(false);
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInputText(transcript);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      if (event.error === 'not-allowed') {
        alert('Microphone access denied. Please enable microphone permissions.');
      }
    };

    recognition.start();
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(inputText);
    }
  };

  const getProgressLabel = () => {
    const labels = {
      intake: 'Understanding your situation',
      analysis: 'Analyzing your rights',
      document: 'Preparing your documents',
      complete: 'Your action plan is ready'
    };
    return labels[currentStage] || 'Getting started';
  };

  const getProgressStep = () => {
    const steps = {
      intake: 1,
      analysis: 2,
      document: 3,
      complete: 4
    };
    return steps[currentStage] || 1;
  };

  if (showSafetyBlock) {
    return <SafetyBlockScreen />;
  }

  return (
    <div className="flex flex-col h-screen bg-slate-900">
      <ProgressTracker 
        currentStep={getProgressStep()}
        totalSteps={4}
        label={getProgressLabel()}
      />

      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-4 scrollbar-hide">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((msg, idx) => (
            <MessageBubble
              key={idx}
              message={msg.message}
              sender={msg.sender}
              timestamp={msg.timestamp}
            />
          ))}
          
          {isTyping && <TypingIndicator />}
          
          {showEmergencyPanel && (
            <EmergencyPanel state={localStorage.getItem('state') || 'KA'} />
          )}
          
          {chips.length > 0 && !isTyping && (
            <ChipOptions options={chips} onSelect={handleChipSelect} />
          )}
          
          <div ref={messagesEndRef} />
        </div>
      </div>

      <div className="border-t border-slate-700 bg-slate-800 shadow-2xl">
        <div className="max-w-4xl mx-auto px-4 py-4">
          <div className="flex gap-3 items-end">
            <div className="flex-1 relative">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder={isListening ? 'Listening...' : 'Type your message...'}
                disabled={isListening}
                className="w-full px-5 py-3.5 bg-slate-700 text-white placeholder-slate-400 border border-slate-600 rounded-2xl focus:outline-none focus:ring-2 focus:ring-amber-500 focus:border-transparent text-base transition-all duration-200 disabled:opacity-50"
              />
            </div>
            
            <button
              onClick={startVoiceInput}
              disabled={isListening}
              className={`p-3.5 rounded-2xl transition-all duration-200 shadow-lg ${
                isListening 
                  ? 'bg-red-600 text-white animate-pulse shadow-red-500/50' 
                  : 'bg-slate-700 hover:bg-slate-600 text-amber-400 hover:text-amber-300 border border-slate-600 hover:border-amber-500/50'
              }`}
              title="Voice input"
            >
              <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M7 4a3 3 0 016 0v4a3 3 0 11-6 0V4zm4 10.93A7.001 7.001 0 0017 8a1 1 0 10-2 0A5 5 0 015 8a1 1 0 00-2 0 7.001 7.001 0 006 6.93V17H6a1 1 0 100 2h8a1 1 0 100-2h-3v-2.07z" clipRule="evenodd" />
              </svg>
            </button>
            
            <button
              onClick={() => handleSendMessage(inputText)}
              disabled={!inputText.trim() || isTyping}
              className="px-6 py-3.5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-900 rounded-2xl font-semibold disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-lg shadow-amber-500/30 hover:shadow-amber-500/50 disabled:shadow-none text-base"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatScreen;

// Made with Bob

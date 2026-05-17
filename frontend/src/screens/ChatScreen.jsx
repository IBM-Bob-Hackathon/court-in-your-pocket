import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import useAppStore from '../store/useAppStore';
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
  
  const { sessionId, language: storeLanguage } = useAppStore();
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [chips, setChips] = useState([]);
  const [currentStage, setCurrentStage] = useState('intake');
  const [showSafetyBlock, setShowSafetyBlock] = useState(false);
  const [showEmergencyPanel, setShowEmergencyPanel] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [language, setLanguage] = useState(storeLanguage || 'en');

  // User details form state (shown inline in chat after intake completes)
  const [userName, setUserName] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [emailId, setEmailId] = useState('');
  const [detailsError, setDetailsError] = useState('');

  // Auto-scroll to latest message
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  // Get sessionId from Zustand store on mount
  useEffect(() => {
    // If no session in store, redirect to welcome
    if (!sessionId) {
      navigate('/welcome', { replace: true });
      return;
    }
    setLanguage(storeLanguage || 'en');
    // Send initial greeting
    sendInitialGreeting(sessionId);
  }, [sessionId, storeLanguage, navigate]);

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
      // If session expired or not found, go back to onboarding to create a new one
      if (error.message && error.message.includes('404')) {
        navigate('/welcome', { replace: true });
        return;
      }
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

      // Check for stage transition to analysis — inject inline form card into chat
      if (response.stage === 'analysis') {
        setMessages(prev => [...prev, { sender: 'user-details-form', timestamp: new Date() }]);
        setChips([]);
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

  const handleUserDetailsSubmit = async () => {
    if (!userName.trim() || !phoneNumber.trim()) {
      setDetailsError('Please fill in the mandatory fields marked with *');
      return;
    }
    if (!/^\d{10}$/.test(phoneNumber.replace(/[\s\-+]/g, ''))) {
      setDetailsError('Please enter a valid 10-digit phone number');
      return;
    }
    setDetailsError('');

    // Save to localStorage for Dev 3
    localStorage.setItem('user_name', userName.trim());
    localStorage.setItem('phone_number', phoneNumber.trim());
    localStorage.setItem('email_id', emailId.trim());

    // Persist to backend session
    try {
      await chatAPI.saveUserDetails(sessionId, {
        user_name: userName.trim(),
        phone_number: phoneNumber.trim(),
        email_id: emailId.trim(),
      });
    } catch (err) {
      console.warn('Could not save user details to session:', err);
    }

    // Remove form card, add Bob closing message, then navigate
    setMessages(prev => [
      ...prev.filter(m => m.sender !== 'user-details-form'),
      {
        sender: 'bob',
        message: `Thank you, ${userName.trim()}! I've noted all your details. I now have everything I need to analyze your legal situation.`,
        timestamp: new Date(),
      }
    ]);

    setTimeout(() => navigate('/rights'), 1800);
  };

  const handleChipSelect = (chip) => {
    handleSendMessage(chip);
  };

  const startVoiceInput = () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      const errorMessage = {
        sender: 'bob',
        message: 'Voice input is only supported in Chrome or Edge. Please type your message instead.',
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
      return;
    }

    const recognition = new SpeechRecognition();
    recognition.lang = language === 'hi' ? 'hi-IN' : 'en-IN';
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.maxAlternatives = 1;

    recognition.onstart = () => {
      setIsListening(true);
    };

    recognition.onend = () => {
      setIsListening(false);
    };
    
    recognition.onresult = (event) => {
      const transcript = event.results[0][0].transcript;
      setInputText(transcript);
      setTimeout(() => {
        handleSendMessage(transcript);
      }, 800);
    };

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      if (event.error === 'not-allowed') {
        const errorMessage = {
          sender: 'bob',
          message: 'Microphone access was denied. Please allow microphone permissions in your browser settings.',
          timestamp: new Date(),
        };
        setMessages(prev => [...prev, errorMessage]);
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
    <div className="relative flex flex-col h-screen max-h-screen overflow-hidden bg-slate-900">
      <ProgressTracker
        currentStep={getProgressStep()}
        totalSteps={4}
        label={getProgressLabel()}
      />

      <div className="flex-1 overflow-y-auto min-h-0 px-3 py-4">
        <div className="max-w-4xl mx-auto space-y-4">
          {messages.map((msg, idx) => (
            msg.sender === 'user-details-form' ? (
              <div key={idx} className="max-w-sm bg-slate-800 border border-amber-500/40 rounded-2xl p-5 shadow-lg">
                <h3 className="text-amber-400 font-bold text-lg mb-1">Almost done!</h3>
                <p className="text-slate-400 text-sm mb-4">
                  Please share your contact details so we can send you a complete summary of your case.
                </p>
                <div className="flex flex-col gap-3">
                  <div className="flex flex-col gap-1">
                    <label className="text-slate-300 text-sm font-medium">
                      User Name <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="text"
                      value={userName}
                      onChange={e => setUserName(e.target.value)}
                      placeholder="Enter your full name"
                      className="bg-slate-700 text-white border border-slate-600 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-amber-400 placeholder-slate-500 text-sm"
                    />
                  </div>
                  <div className="flex flex-col gap-1">
                    <label className="text-slate-300 text-sm font-medium">
                      Phone Number <span className="text-red-400">*</span>
                    </label>
                    <input
                      type="tel"
                      value={phoneNumber}
                      onChange={e => setPhoneNumber(e.target.value)}
                      placeholder="10-digit mobile number"
                      maxLength={10}
                      className="bg-slate-700 text-white border border-slate-600 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-amber-400 placeholder-slate-500 text-sm"
                    />
                  </div>
                  <div className="flex flex-col gap-1">
                    <label className="text-slate-300 text-sm font-medium">
                      Email ID <span className="text-slate-500 text-xs">(optional)</span>
                    </label>
                    <input
                      type="email"
                      value={emailId}
                      onChange={e => setEmailId(e.target.value)}
                      placeholder="your@email.com"
                      className="bg-slate-700 text-white border border-slate-600 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-amber-400 placeholder-slate-500 text-sm"
                    />
                  </div>
                  <button
                    onClick={handleUserDetailsSubmit}
                    className="bg-amber-500 hover:bg-amber-600 text-slate-900 font-bold py-2.5 rounded-xl transition-colors mt-1 text-sm"
                  >
                    Submit &amp; Continue
                  </button>
                  {detailsError && (
                    <p className="text-red-400 text-sm text-center -mt-1">{detailsError}</p>
                  )}
                </div>
              </div>
            ) : (
              <MessageBubble
                key={idx}
                message={msg.message}
                sender={msg.sender}
                timestamp={msg.timestamp}
              />
            )
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

      <div className="flex-shrink-0 bg-slate-800/95 backdrop-blur-sm border-t border-slate-700/50 shadow-[0_-4px_20px_rgba(0,0,0,0.4)] px-4 py-3">
        <div className="max-w-4xl mx-auto">
          <div className="flex items-end gap-2 bg-slate-700/80 border border-slate-600/50 rounded-2xl px-4 py-2 focus-within:border-amber-500/60 focus-within:ring-1 focus-within:ring-amber-500/30 transition-all duration-200">
            <textarea
              rows={1}
              value={inputText}
              onChange={(e) => setInputText(e.target.value)}
              onInput={(e) => {
                e.target.style.height = 'auto';
                e.target.style.height = Math.min(e.target.scrollHeight, 112) + 'px';
              }}
              onKeyPress={handleKeyPress}
              placeholder={isListening ? '🎙️  Listening...' : 'Ask your legal question...'}
              disabled={isListening || messages.some(m => m.sender === 'user-details-form')}
              className="flex-1 bg-transparent text-white text-base placeholder-slate-400 focus:outline-none py-1 leading-relaxed min-h-[28px] max-h-28 resize-none overflow-hidden"
            />
            
            <button
              onClick={startVoiceInput}
              disabled={isListening}
              className="p-3 rounded-xl transition-all duration-200 flex-shrink-0"
              style={isListening
                ? { backgroundColor: 'rgba(239, 68, 68, 0.2)', color: '#ef4444', animation: 'pulse 2s cubic-bezier(0.4, 0, 0.6, 1) infinite' }
                : { backgroundColor: '#475569', color: '#94a3b8' }
              }
              title="Voice input"
            >
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" y1="19" x2="12" y2="23"/>
                <line x1="8" y1="23" x2="16" y2="23"/>
              </svg>
            </button>
            
            <button
              onClick={() => handleSendMessage(inputText)}
              disabled={!inputText.trim() || isTyping}
              className="p-3 rounded-xl transition-all duration-200 flex-shrink-0"
              style={{
                backgroundColor: (!inputText.trim() || isTyping) ? '#64748b' : '#f59e0b',
                color: '#0f172a',
                opacity: (!inputText.trim() || isTyping) ? 0.5 : 1,
                cursor: (!inputText.trim() || isTyping) ? 'not-allowed' : 'pointer',
                boxShadow: (!inputText.trim() || isTyping) ? 'none' : '0 4px 6px -1px rgba(245, 158, 11, 0.3)'
              }}
              title="Send message"
            >
              <svg className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M22 2L11 13"/>
                <path d="M22 2L15 22 11 13 2 9l20-7z"/>
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatScreen;

// Made with Bob

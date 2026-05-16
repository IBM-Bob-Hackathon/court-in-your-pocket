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
    <div className="flex flex-col h-screen max-h-screen overflow-hidden bg-slate-900">
      <ProgressTracker
        currentStep={getProgressStep()}
        totalSteps={4}
        label={getProgressLabel()}
      />

      <div className="flex-1 overflow-y-auto min-h-0 px-3 py-4">
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
              disabled={isListening}
              className="flex-1 bg-transparent text-white text-base placeholder-slate-400 focus:outline-none py-1 leading-relaxed min-h-[28px] max-h-28 resize-none overflow-hidden"
            />
            
            <button
              onClick={startVoiceInput}
              disabled={isListening}
              className={isListening
                ? 'p-2 rounded-xl bg-red-500/20 text-red-400 animate-pulse'
                : 'p-2 rounded-xl text-slate-400 hover:text-amber-400 hover:bg-slate-600/50 transition-all duration-200'
              }
              title="Voice input"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <path d="M12 1a3 3 0 0 0-3 3v8a3 3 0 0 0 6 0V4a3 3 0 0 0-3-3z"/>
                <path d="M19 10v2a7 7 0 0 1-14 0v-2"/>
                <line x1="12" y1="19" x2="12" y2="23"/>
                <line x1="8" y1="23" x2="16" y2="23"/>
              </svg>
            </button>
            
            <button
              onClick={() => handleSendMessage(inputText)}
              disabled={!inputText.trim() || isTyping}
              className="p-2 rounded-xl bg-amber-500 hover:bg-amber-400 active:scale-95 text-slate-900 transition-all duration-200 shadow-md shadow-amber-500/30 disabled:opacity-40 disabled:cursor-not-allowed disabled:shadow-none flex-shrink-0"
              title="Send message"
            >
              <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
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

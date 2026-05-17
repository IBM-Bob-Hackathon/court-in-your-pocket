import { createContext, useContext, useState } from 'react';

const AppContext = createContext();

export const AppProvider = ({ children }) => {
  const [sessionId, setSessionId] = useState(null);
  const [language, setLanguage] = useState('en');
  const [state, setState] = useState(null);
  const [stage, setStage] = useState('landing');

  const value = {
    sessionId,
    setSessionId,
    language,
    setLanguage,
    state,
    setState,
    stage,
    setStage,
  };

  return <AppContext.Provider value={value}>{children}</AppContext.Provider>;
};

export const useAppContext = () => {
  const context = useContext(AppContext);
  if (!context) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
};

// Made with Bob

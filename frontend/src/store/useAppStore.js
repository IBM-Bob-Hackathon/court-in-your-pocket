import { create } from 'zustand';
import { persist } from 'zustand/middleware';

const useAppStore = create(
  persist(
    (set) => ({
      // Session data
      sessionId: null,
      language: 'en',
      state: null,
      stage: 'landing', // landing | intake | analysis | document | complete
      
      // Actions
      setSessionId: (sessionId) => set({ sessionId }),
      setLanguage: (language) => set({ language }),
      setState: (state) => set({ state }),
      setStage: (stage) => set({ stage }),
      
      // Reset session
      resetSession: () => set({
        sessionId: null,
        state: null,
        stage: 'landing',
      }),
      
      // Initialize session
      initializeSession: (sessionId, language, state) => set({
        sessionId,
        language,
        state,
        stage: 'intake',
      }),
    }),
    {
      name: 'court-in-pocket-storage',
      partialize: (state) => ({
        language: state.language,
        sessionId: state.sessionId,
        state: state.state,
        stage: state.stage,
      }),
    }
  )
);

export default useAppStore;

// Made with Bob

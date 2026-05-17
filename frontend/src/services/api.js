const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const chatAPI = {
  /**
   * Create a new session
   * @param {string} language - Language preference (default: 'en')
   * @param {string} state - State code (default: 'KA')
   * @returns {Promise<Object>} Session data with sessionId
   */
  async createSession(language = 'en', state = 'KA') {
    try {
      console.log('🔵 Creating new session:', { language, state, url: `${API_BASE_URL}/api/chat/init` });
      
      const response = await fetch(`${API_BASE_URL}/api/chat/init`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ language, state }),
      });

      console.log('🔵 Session creation response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('🔴 Session creation error:', errorText);
        throw new Error(`Failed to create session: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log('🟢 Session created:', data);
      return data;
    } catch (error) {
      console.error('🔴 Failed to create session:', error);
      throw error;
    }
  },

  /**
   * Send a message to Bob
   * @param {string} sessionId - Current session ID
   * @param {string} message - User's message
   * @returns {Promise<Object>} Bob's response
   */
  async sendMessage(sessionId, message) {
    try {
      console.log('🔵 Sending message to backend:', { sessionId, message, url: `${API_BASE_URL}/api/chat/message` });
      
      const response = await fetch(`${API_BASE_URL}/api/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ sessionId, message }),
      });

      console.log('🔵 Response status:', response.status);

      if (!response.ok) {
        const errorText = await response.text();
        console.error('🔴 API error response:', errorText);
        throw new Error(`API error: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log('🟢 API response data:', data);
      return data;
    } catch (error) {
      console.error('🔴 Failed to send message:', error);
      throw error;
    }
  },
};

export default chatAPI;

// Made with Bob

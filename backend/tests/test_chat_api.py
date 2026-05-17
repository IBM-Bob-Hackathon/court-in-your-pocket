"""
Test suite for Chat API endpoints
Run with: pytest backend/tests/test_chat_api.py
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from session_store import create_session, delete_session

client = TestClient(app)


class TestChatAPI:
    """Test cases for /api/chat/message endpoint"""
    
    def setup_method(self):
        """Setup test session before each test"""
        self.session = create_session(language="en", state="KA")
        self.session_id = self.session["sessionId"]
    
    def teardown_method(self):
        """Cleanup after each test"""
        delete_session(self.session_id)
    
    def test_initial_greeting(self):
        """Test initial greeting request"""
        response = client.post(
            "/api/chat/message",
            json={"sessionId": self.session_id, "message": "__INIT__"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert data["stage"] == "intake"
        assert data["safetyBlocked"] == False
        assert "Namaste" in data["reply"] or "legal issue" in data["reply"]
    
    def test_normal_message(self):
        """Test normal user message"""
        response = client.post(
            "/api/chat/message",
            json={"sessionId": self.session_id, "message": "My landlord is not returning my deposit"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "reply" in data
        assert data["stage"] == "intake"
        assert data["safetyBlocked"] == False
        assert "extractedFacts" in data
    
    def test_safety_block(self):
        """Test safety blocking for dangerous content"""
        response = client.post(
            "/api/chat/message",
            json={"sessionId": self.session_id, "message": "How do I hide evidence from police?"}
        )
        assert response.status_code == 200
        data = response.json()
        assert data["safetyBlocked"] == True
    
    def test_invalid_session(self):
        """Test with invalid session ID"""
        response = client.post(
            "/api/chat/message",
            json={"sessionId": "invalid-session-id", "message": "Hello"}
        )
        assert response.status_code == 404
    
    def test_fact_extraction(self):
        """Test that facts are extracted from messages"""
        # First message
        response1 = client.post(
            "/api/chat/message",
            json={"sessionId": self.session_id, "message": "My landlord in Bangalore is not returning my 50000 rupee deposit"}
        )
        assert response1.status_code == 200
        data1 = response1.json()
        facts = data1["extractedFacts"]
        
        # Should extract issue, location, and amount
        assert facts.get("issue") is not None or "deposit" in str(facts)
        assert facts.get("location") is not None or facts.get("amount") is not None
    
    def test_stage_transition(self):
        """Test transition from intake to analysis stage"""
        # Simulate multiple messages to collect facts
        messages = [
            "My landlord is not returning my deposit",
            "Bangalore",
            "50000 rupees",
            "2 months ago",
            "Mr. Sharma"
        ]
        
        for msg in messages:
            response = client.post(
                "/api/chat/message",
                json={"sessionId": self.session_id, "message": msg}
            )
            assert response.status_code == 200
            data = response.json()
            
            # Last message should trigger transition to analysis
            if msg == messages[-1]:
                assert data["stage"] in ["intake", "analysis"]


class TestChatComponents:
    """Test individual chat components"""
    
    def test_conversation_history_trimming(self):
        """Test that conversation history is trimmed properly"""
        from utils.stage_orchestrator import trim_conversation_history
        
        # Create history with 25 messages
        history = [{"role": "user", "content": f"Message {i}"} for i in range(25)]
        
        trimmed = trim_conversation_history(history, max_messages=20)
        
        assert len(trimmed) == 20
        assert trimmed[0] == history[0]  # First message preserved
        assert trimmed[-1] == history[-1]  # Last message preserved
    
    def test_should_transition_to_analysis(self):
        """Test stage transition logic"""
        from utils.stage_orchestrator import should_transition_to_analysis
        
        # Not enough facts
        facts1 = {"issue": "deposit", "location": None, "amount": None}
        assert should_transition_to_analysis(facts1) == False
        
        # Enough facts
        facts2 = {"issue": "deposit", "location": "Bangalore", "amount": "50000", "dates": ["2 months ago"]}
        assert should_transition_to_analysis(facts2) == True
    
    def test_question_counting(self):
        """Test intake question counting"""
        from utils.stage_orchestrator import count_intake_questions
        
        history = [
            {"role": "assistant", "content": "What is your issue?"},
            {"role": "user", "content": "Deposit not returned"},
            {"role": "assistant", "content": "Which city?"},
            {"role": "user", "content": "Bangalore"},
            {"role": "assistant", "content": "How much was the amount?"}
        ]
        
        count = count_intake_questions(history)
        assert count == 3  # Three questions from Bob


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob

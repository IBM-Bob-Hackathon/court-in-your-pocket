# Pocket Court Backend API

AI-powered legal assistant backend for India, built with FastAPI, OpenAI, and LangChain.

## 🚀 Features

### Implemented Endpoints

#### 1. Action Plan Generator (`POST /api/action-plan/generate`)
Generates AI-powered, step-by-step action plans for legal issues using OpenAI's structured outputs.

**Request:**
```json
{
  "sessionId": "session_123",
  "category": "Tenant Rights",
  "sub_scenario": "Security Deposit Not Returned",
  "option": "A"
}
```

**Options:**
- `A` - Demand Letter
- `B` - File Complaint
- `C` - Free Legal Aid

**Response:**
```json
{
  "steps": [
    {
      "step_number": 1,
      "instruction": "Draft a formal demand letter...",
      "time_estimate": "2-3 hours"
    }
  ]
}
```

#### 2. Document Generator (`POST /api/document/generate`)
Generates legal documents by replacing template placeholders with user data.

**Request:**
```json
{
  "sessionId": "session_123"
}
```

**Response:**
```json
{
  "documentText": "Dear John Doe,\n\nThis is a formal notice..."
}
```

## 📁 Project Structure

```
backend/
├── agents/
│   └── action_plan_agent.py    # AI agents and business logic
├── routers/
│   └── action_plan.py          # FastAPI route definitions
├── templates/
│   └── demand_letter_generic.txt  # Document templates
├── data/
│   └── (session data storage)
└── main.py                     # FastAPI application entry point
```

## 🛠️ Architecture

### Action Plan Agent
- Uses OpenAI's `gpt-4o-2024-08-06` model with structured outputs
- Generates 4-5 actionable steps tailored to Indian law
- Includes realistic time estimates for each step
- Context-aware based on user's extracted facts

### Document Generator
- Template-based document generation
- Pure string replacement of `{{placeholders}}`
- Supports multiple document types (demand letters, complaints, legal aid applications)
- Fallback to generic templates if specific ones don't exist

### Session Management
- Mock in-memory session storage (replace with database in production)
- Stores user's extracted facts and context
- Session data structure:
  ```python
  {
    "extractedFacts": {
      "landlord_name": "John Doe",
      "tenant_name": "Rajesh Kumar",
      "deposit_amount": "40000",
      ...
    },
    "category": "Tenant Rights",
    "sub_scenario": "Security Deposit Not Returned",
    "option": "A"
  }
  ```

## 🔧 Setup & Installation

### Prerequisites
- Python 3.9+
- OpenAI API key

### Installation

1. **Install dependencies:**
```bash
pip install fastapi uvicorn openai pydantic python-dotenv
```

2. **Set environment variables:**
```bash
# Create .env file
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

3. **Run the server:**
```bash
# From the project root directory
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000

# OR from the backend directory
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

4. **Access the API:**
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## 📝 Usage Examples

### Generate Action Plan

```bash
curl -X POST "http://localhost:8000/api/action-plan/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "session_123",
    "category": "Tenant Rights",
    "sub_scenario": "Security Deposit Not Returned",
    "option": "A"
  }'
```

### Generate Document

```bash
curl -X POST "http://localhost:8000/api/document/generate" \
  -H "Content-Type: application/json" \
  -d '{
    "sessionId": "session_123"
  }'
```

### Health Check

```bash
curl "http://localhost:8000/api/action-plan/health"
```

## 🔐 Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `OPENAI_API_KEY` | OpenAI API key for LLM access | Yes |

## 🧪 Testing

### Test with Mock Data

The implementation includes mock session data for testing:

```python
MOCK_SESSIONS = {
    "session_123": {
        "extractedFacts": {
            "landlord_name": "John Doe",
            "tenant_name": "Rajesh Kumar",
            "deposit_amount": "40000",
            "city": "Bangalore",
            ...
        },
        "category": "Tenant Rights",
        "sub_scenario": "Security Deposit Not Returned",
        "option": "A"
    }
}
```

Use `sessionId: "session_123"` for testing.

## 📋 Template System

### Creating New Templates

1. Create a new `.txt` file in `backend/templates/`
2. Use `{{placeholder}}` syntax for dynamic content
3. Name format: `{category_slug}_{template_type}.txt`
   - Example: `tenant_rights_demand_letter.txt`

### Template Placeholders

Common placeholders:
- `{{landlord_name}}`
- `{{tenant_name}}`
- `{{deposit_amount}}`
- `{{city}}`
- `{{property_address}}`
- `{{lease_start_date}}`
- `{{lease_end_date}}`
- `{{notice_date}}`

## 🚀 Production Considerations

### Replace Mock Data
Replace `MOCK_SESSIONS` in `action_plan_agent.py` with actual database queries:

```python
def get_session_data(session_id: str) -> Optional[Dict]:
    # Replace with your database query
    session = db.query(Session).filter(Session.id == session_id).first()
    return session.to_dict() if session else None
```

### Security
- Add authentication/authorization middleware
- Validate and sanitize all user inputs
- Rate limit API endpoints
- Use environment-specific CORS settings

### Monitoring
- Add logging for all LLM calls
- Track token usage and costs
- Monitor API response times
- Set up error alerting

### Scaling
- Implement caching for frequently generated plans
- Use async database queries
- Consider LLM response streaming for better UX
- Add request queuing for high load

## 📚 API Documentation

Full interactive API documentation is available at `/docs` when the server is running.

## 🤝 Integration with Frontend

The API is designed to work seamlessly with the React frontend:

1. Frontend collects user information through chat
2. Backend stores data in `extractedFacts`
3. User selects an option (A, B, or C)
4. Frontend calls `/api/action-plan/generate`
5. User reviews the plan
6. Frontend calls `/api/document/generate` to create the document

## 📄 License

Part of the Pocket Court project - AI Legal Assistant for India.

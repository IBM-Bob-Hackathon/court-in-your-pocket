# Court in Your Pocket 🏛️

**AI-Powered Legal Assistance for Indian Citizens**

Court in Your Pocket is an intelligent legal assistance platform that helps Indian citizens understand their legal rights, navigate legal processes, and take appropriate action when facing legal issues. The system uses IBM watsonx AI to provide personalized, context-aware legal guidance across multiple Indian states and languages.

---

## 📋 Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [System Components](#system-components)
- [User Journey](#user-journey)
- [API Documentation](#api-documentation)
- [Configuration](#configuration)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

---

## 🎯 Overview

### Problem Statement

Many Indian citizens face legal issues but lack access to affordable legal advice. They often don't know:
- What their legal rights are
- Whether their situation has legal merit
- What steps to take next
- How to document their case
- Where to seek help

### Solution

Court in Your Pocket provides:
1. **Intelligent Intake**: AI-powered conversation to understand the user's legal issue
2. **Legal Analysis**: Classification of the issue and identification of applicable laws
3. **Rights Education**: Clear explanation of relevant legal rights
4. **Action Planning**: Step-by-step guidance on what to do next
5. **Document Generation**: Automated creation of legal documents (demand letters, complaints)
6. **Safety Monitoring**: Detection of emergency situations requiring immediate intervention

---

## ✨ Key Features

### 🌐 Multi-Language Support
- English, Hindi, Tamil, Telugu, Kannada, Marathi, Bengali, Gujarati
- Real-time language switching
- Culturally appropriate responses

### 🗺️ State-Specific Legal Information
- Karnataka (KA)
- Maharashtra (MH)
- Delhi (DL)
- Extensible to other states

### 🤖 AI-Powered Agents
- **Intake Agent**: Collects case details through natural conversation
- **Classifier Agent**: Identifies legal category (tenant, consumer, employment)
- **Analysis Agent**: Determines applicable laws and violations
- **Safety Agent**: Monitors for emergency situations
- **Action Plan Agent**: Generates personalized action plans

### 🛡️ Safety Features
- Real-time detection of:
  - Self-harm ideation
  - Criminal intent
  - Evidence tampering
  - Threats or violence
- Emergency contact information
- Crisis intervention resources

### 📄 Document Generation
- Demand letters
- Legal notices
- Complaint templates
- PDF export functionality

---

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React + Vite)                  │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐     │
│  │ Landing  │  │   Chat   │  │  Rights  │  │  Action  │     │
│  │  Screen  │  │  Screen  │  │  Screen  │  │   Plan   │     │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘     │
│         │              │              │              │      │
│         └──────────────┴──────────────┴──────────────┘      │
│                        │                                    │
│                   Zustand Store                             │
│         (Session, Language, State, Stage)                   │
└────────────────────────┬────────────────────────────────────┘
                         │ REST API (JSON)
                         │
┌────────────────────────┴────────────────────────────────────┐
│                    Backend (FastAPI)                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │           Session Management Layer                   │   │
│  │      (In-Memory Store with Auto-Cleanup)             │   │
│  └──────────────────────────────────────────────────────┘   │
│                         │                                   │
│  ┌──────────────────────┴────────────────────────────────┐  │
│  │                  API Routers                           │ │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐              │ │
│  │  │ Session  │  │   Chat   │  │  Legal   │              │ │
│  │  │  Router  │  │  Router  │  │  Router  │              │ │
│  │  └──────────┘  └──────────┘  └──────────┘              │ │
│  │  ┌──────────┐                                          │ │
│  │  │  Action  │                                          │ │
│  │  │   Plan   │                                          │ │
│  │  └──────────┘                                          │ │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                   │
│  ┌──────────────────────┴────────────────────────────────┐  │
│  │                  AI Agents Layer                      │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │  │
│  │  │  Intake  │  │Classifier│  │ Analysis │             │  │
│  │  │  Agent   │  │  Agent   │  │  Agent   │             │  │
│  │  └──────────┘  └──────────┘  └──────────┘             │  │
│  │  ┌──────────┐  ┌──────────┐                           │  │
│  │  │  Safety  │  │  Action  │                           │  │
│  │  │  Agent   │  │   Plan   │                           │  │
│  │  └──────────┘  └──────────┘                           │  │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                   │
│  ┌──────────────────────┴────────────────────────────────┐  │
│  │              IBM watsonx.ai Integration               │  │
│  │         Model: meta-llama/llama-3-3-70b-instruct      │  │
│  └────────────────────────────────────────────────────────┘ │
│                         │                                   │
│  ┌──────────────────────┴────────────────────────────────┐  │
│  │                Legal Data Services                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐             │  │
│  │  │  Tenant  │  │ Consumer │  │Employment│             │  │
│  │  │   Laws   │  │   Laws   │  │   Laws   │             │  │
│  │  └──────────┘  └──────────┘  └──────────┘             │  │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

```
User Input → Landing Screen → Session Creation → Chat Interface
                                      ↓
                              Session Store (Backend)
                                      ↓
                    ┌─────────────────┴─────────────────┐
                    ↓                                     ↓
            Safety Check                          Intake Agent
                    ↓                                     ↓
            Emergency?                          Collect Facts
                    ↓                                     ↓
            Yes → Block                         Classifier Agent
                    ↓                                     ↓
            No → Continue                    Identify Category
                                                         ↓
                                              Analysis Agent
                                                         ↓
                                            Find Applicable Laws
                                                         ↓
                                    ┌───────────────────┴───────────────────┐
                                    ↓                                       ↓
                            Rights Screen                          Action Plan Screen
                         (Display Rights)                      (Generate Action Plan)
                                                                           ↓
                                                              Document Generation
```

---

## 💻 Technology Stack

### Frontend
- **Framework**: React 19.2.6
- **Build Tool**: Vite 8.0.12
- **Routing**: React Router DOM 7.15.1
- **State Management**: Zustand 5.0.13
- **Styling**: Tailwind CSS 3.4.19
- **Markdown**: React Markdown 10.1.0
- **PDF Generation**: jsPDF 2.5.2

### Backend
- **Framework**: FastAPI 0.115.0
- **Server**: Uvicorn 0.32.0
- **AI Integration**: IBM watsonx.ai SDK 1.1.0+
- **Data Validation**: Pydantic 2.9.0
- **Environment**: Python-dotenv 1.0.1
- **HTTP Client**: httpx 0.27.0+

### AI/ML
- **Platform**: IBM watsonx.ai
- **Model**: meta-llama/llama-3-3-70b-instruct
- **Capabilities**:
  - Natural language understanding
  - Multi-language support
  - Context-aware responses
  - Legal domain knowledge

---

## 📁 Project Structure

```
court-in-your-pocket/
├── frontend/                      # React frontend application
│   ├── src/
│   │   ├── screens/              # Screen components
│   │   │   ├── LandingScreen.jsx # Welcome/onboarding
│   │   │   ├── ChatScreen.jsx    # Chat interface
│   │   │   ├── RightsScreen.jsx  # Legal rights display
│   │   │   ├── ActionPlanScreen.jsx # Action plan
│   │   │   └── ErrorBoundary.jsx # Error handling
│   │   ├── store/
│   │   │   └── useAppStore.js    # Zustand global state
│   │   ├── services/
│   │   │   └── api.js            # API client
│   │   ├── App.jsx               # Main app component
│   │   └── main.jsx              # Entry point
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── .env.example
│
├── backend/                       # FastAPI backend
│   ├── agents/                   # AI agent implementations
│   │   ├── watsonx_client.py    # IBM watsonx integration
│   │   ├── intake_agent.py      # Fact collection
│   │   ├── classifier_agent.py  # Category identification
│   │   ├── analysis_agent.py    # Legal analysis
│   │   ├── safety_agent.py      # Safety monitoring
│   │   └── action_plan_agent.py # Action plan generation
│   ├── routers/                  # API route handlers
│   │   ├── session.py           # Session management
│   │   ├── chat.py              # Chat endpoints
│   │   ├── legal.py             # Legal data endpoints
│   │   └── action_plan.py       # Action plan endpoints
│   ├── services/
│   │   └── legal_data_service.py # Legal data access
│   ├── session/
│   │   ├── session.py           # Session model
│   │   └── session_store.py     # Session storage
│   ├── data/                     # Legal knowledge base
│   │   ├── tenant_laws.json
│   │   ├── consumer_laws.json
│   │   └── employment_laws.json
│   ├── templates/                # Document templates
│   │   ├── template_demand_letter_tenant.txt
│   │   ├── template_demand_letter_consumer.txt
│   │   └── template_demand_letter_employment.txt
│   ├── main.py                   # FastAPI application
│   ├── requirements.txt
│   └── .env.example
│
└── docs/                          # Documentation
    ├── README.md
    ├── SETUP_INSTRUCTIONS.md
    ├── DATA_FLOW.md
    └── QUICKSTART.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.9+ (for backend)
- **IBM watsonx.ai** account with API credentials
- **Git** (for version control)

### Quick Start

#### 1. Clone the Repository

```bash
git clone <repository-url>
cd court-in-your-pocket
```

#### 2. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from example
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux

# Edit .env and add your IBM watsonx credentials:
# IBM_WATSONX_API_KEY=your_api_key_here
# IBM_WATSONX_PROJECT_ID=your_project_id_here
# IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Start the backend server
uvicorn main:app --reload --port 8000
```

Backend will be available at: `http://localhost:8000`
API Documentation: `http://localhost:8000/docs`

#### 3. Frontend Setup

```bash
# Open new terminal
cd frontend

# Install dependencies
npm install

# Create .env file from example
copy .env.example .env  # Windows
cp .env.example .env    # Mac/Linux

# Start development server
npm run dev
```

Frontend will be available at: `http://localhost:5173`

#### 4. Verify Installation

1. Open browser to `http://localhost:5173`
2. You should see the Landing screen
3. Select a state and language
4. Click "Get Started"
5. You should be redirected to the Chat screen

---

## 🧩 System Components

### Frontend Components

#### 1. Landing Screen (`/welcome`)
- **Purpose**: User onboarding and session initialization
- **Features**:
  - State selection (Karnataka, Maharashtra, Delhi)
  - Language selection (8+ languages)
  - Session creation
  - Disclaimer display
- **State Management**: Initializes Zustand store with session data

#### 2. Chat Screen (`/chat`)
- **Purpose**: Interactive conversation for case intake
- **Features**:
  - Real-time messaging
  - AI-powered responses
  - Safety monitoring
  - Progress tracking
  - Emergency intervention
- **Agents Used**: Intake Agent, Safety Agent, Classifier Agent

#### 3. Rights Screen (`/rights`)
- **Purpose**: Display applicable legal rights
- **Features**:
  - Category-specific rights
  - State-specific information
  - Multi-language support
  - Markdown rendering
- **Data Source**: Legal data service

#### 4. Action Plan Screen (`/action`)
- **Purpose**: Generate and display action plan
- **Features**:
  - Step-by-step guidance
  - Document generation
  - PDF export
  - Timeline creation
- **Agents Used**: Action Plan Agent, Analysis Agent

### Backend Components

#### 1. Session Management
- **File**: `session/session_store.py`
- **Purpose**: Manage user sessions
- **Features**:
  - In-memory session storage
  - Automatic cleanup of expired sessions
  - Session data persistence
  - Thread-safe operations

#### 2. AI Agents

##### Intake Agent
- **File**: `agents/intake_agent.py`
- **Purpose**: Collect case facts through conversation
- **Features**:
  - Category-aware questioning
  - Dynamic field collection
  - Context retention
  - Multi-language support

##### Classifier Agent
- **File**: `agents/classifier_agent.py`
- **Purpose**: Identify legal category
- **Categories**:
  - Tenant issues
  - Consumer disputes
  - Employment problems
  - Other legal matters

##### Analysis Agent
- **File**: `agents/analysis_agent.py`
- **Purpose**: Analyze case and identify applicable laws
- **Features**:
  - Law matching
  - Violation identification
  - Evidence assessment
  - Strength evaluation

##### Safety Agent
- **File**: `agents/safety_agent.py`
- **Purpose**: Monitor for emergency situations
- **Detects**:
  - Self-harm ideation
  - Criminal intent
  - Evidence tampering
  - Threats or violence
- **Actions**:
  - Block unsafe content
  - Provide emergency contacts
  - Log incidents

##### Action Plan Agent
- **File**: `agents/action_plan_agent.py`
- **Purpose**: Generate personalized action plans
- **Features**:
  - Step-by-step guidance
  - Document templates
  - Timeline creation
  - Resource links

#### 3. Legal Data Service
- **File**: `services/legal_data_service.py`
- **Purpose**: Access legal knowledge base
- **Data Sources**:
  - `data/tenant_laws.json`
  - `data/consumer_laws.json`
  - `data/employment_laws.json`
- **Features**:
  - State-specific laws
  - Category filtering
  - Law details retrieval

---

## 👤 User Journey

### Complete Flow

```
1. Landing Screen
   ↓
   User selects: State (KA/MH/DL) + Language (EN/HI/etc.)
   ↓
   Click "Get Started"
   ↓
   POST /api/session/start → Returns sessionId
   ↓
   Store in Zustand: {sessionId, language, state, stage: 'intake'}
   ↓
   Navigate to /chat

2. Chat Screen (Intake Phase)
   ↓
   User describes their issue
   ↓
   Safety Agent checks message
   ↓
   Safe? → Continue | Unsafe? → Show emergency contacts
   ↓
   Intake Agent asks clarifying questions
   ↓
   Collect: category, description, dates, parties, evidence
   ↓
   Classifier Agent identifies category
   ↓
   Stage changes to 'analysis'

3. Analysis Phase
   ↓
   Analysis Agent processes case
   ↓
   Identifies applicable laws
   ↓
   Determines violations
   ↓
   Assesses case strength
   ↓
   Stage changes to 'rights'

4. Rights Screen
   ↓
   Display relevant legal rights
   ↓
   Show state-specific information
   ↓
   Explain legal protections
   ↓
   User can navigate to Action Plan

5. Action Plan Screen
   ↓
   Generate personalized action plan
   ↓
   Show step-by-step guidance
   ↓
   Generate documents (demand letter, complaint)
   ↓
   Provide timeline
   ↓
   Export to PDF
```

### Session Lifecycle

```
Session Created → Intake → Classification → Analysis → Rights → Action Plan
     ↓              ↓           ↓              ↓          ↓          ↓
  30 min TTL    Collecting   Identifying   Finding    Displaying  Generating
                  facts      category       laws       rights      plan
```

---

## 📡 API Documentation

### Session Endpoints

#### POST `/api/session/start`
Create a new session.

**Request:**
```json
{
  "language": "en",
  "state": "KA"
}
```

**Response:**
```json
{
  "sessionId": "550e8400-e29b-41d4-a716-446655440000"
}
```

#### GET `/api/session/{sessionId}`
Get session details.

**Response:**
```json
{
  "sessionId": "550e8400-...",
  "language": "en",
  "state": "KA",
  "stage": "intake",
  "createdAt": "2026-05-18T12:00:00Z"
}
```

### Chat Endpoints

#### POST `/api/chat/message`
Send a message and get AI response.

**Request:**
```json
{
  "sessionId": "550e8400-...",
  "message": "My landlord won't return my deposit"
}
```

**Response:**
```json
{
  "response": "I understand. Can you tell me when you moved out?",
  "stage": "intake",
  "safe": true
}
```

### Legal Endpoints

#### GET `/api/legal/rights/{category}`
Get legal rights for a category.

**Parameters:**
- `category`: tenant | consumer | employment
- `state`: KA | MH | DL (query param)

**Response:**
```json
{
  "category": "tenant",
  "state": "KA",
  "rights": [
    {
      "title": "Right to Security Deposit Return",
      "description": "...",
      "law": "Karnataka Rent Control Act"
    }
  ]
}
```

### Action Plan Endpoints

#### POST `/api/action-plan/generate`
Generate action plan.

**Request:**
```json
{
  "sessionId": "550e8400-...",
  "option": "demand_letter"
}
```

**Response:**
```json
{
  "plan": {
    "steps": [...],
    "documents": [...],
    "timeline": "2-4 weeks"
  }
}
```

### Safety Endpoints

#### POST `/api/safety/check`
Check message safety.

**Request:**
```json
{
  "message": "I want to hurt someone"
}
```

**Response:**
```json
{
  "safe": false,
  "emergency": true,
  "reason": "Threat detected",
  "emergency_contacts": {
    "police": "100",
    "helpline": "..."
  }
}
```

---

## ⚙️ Configuration

### Environment Variables

#### Backend (`.env`)

```bash
# IBM watsonx Configuration
IBM_WATSONX_API_KEY=your_api_key_here
IBM_WATSONX_PROJECT_ID=your_project_id_here
IBM_WATSONX_URL=https://us-south.ml.cloud.ibm.com

# Server Configuration
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:5173

# Session Configuration
SESSION_TIMEOUT_MINUTES=30
```

#### Frontend (`.env`)

```bash
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
```

### Model Configuration

Edit `backend/agents/watsonx_client.py`:

```python
DEFAULT_MODEL_ID = "meta-llama/llama-3-3-70b-instruct"
DEFAULT_MAX_TOKENS = 500
DEFAULT_TEMPERATURE = 0.7
```

---

## 🛠️ Development

### Running Tests

#### Backend Tests
```bash
cd backend
pytest tests/
```

#### Frontend Tests
```bash
cd frontend
npm test
```

### Code Style

#### Backend (Python)
- Follow PEP 8
- Use type hints
- Document functions with docstrings

#### Frontend (JavaScript)
- Use ESLint configuration
- Follow React best practices
- Use functional components with hooks

### Adding New Features

#### Adding a New Legal Category

1. Create data file: `backend/data/new_category_laws.json`
2. Update classifier agent: `backend/agents/classifier_agent.py`
3. Add category to intake agent: `backend/agents/intake_agent.py`
4. Create document template: `backend/templates/template_demand_letter_new_category.txt`

#### Adding a New State

1. Update state selector in: `frontend/src/screens/LandingScreen.jsx`
2. Add state-specific laws to data files
3. Update legal data service filters

#### Adding a New Language

1. Add language to: `backend/agents/intake_agent.py` (LANGUAGE_MAP)
2. Update language selector in: `frontend/src/screens/LandingScreen.jsx`
3. Add translations for UI elements

---

## 🐛 Troubleshooting

### Common Issues

#### Backend won't start
```bash
# Check Python version
python --version  # Should be 3.9+

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check environment variables
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('IBM_WATSONX_API_KEY'))"
```

#### Frontend won't start
```bash
# Clear cache
rm -rf node_modules package-lock.json
npm install

# Check Node version
node --version  # Should be 18+
```

#### watsonx connection fails
- Verify API key is correct
- Check project ID is valid
- Ensure watsonx URL is accessible
- Test connection: `curl http://localhost:8000/api/test/watsonx`

#### Session not persisting
- Check browser localStorage
- Clear localStorage: `localStorage.clear()`
- Verify session timeout settings

#### CORS errors
- Verify FRONTEND_URL in backend `.env`
- Check CORS middleware configuration in `backend/main.py`

### Debug Mode

Enable debug logging:

```python
# backend/main.py
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Session count
curl http://localhost:8000/health | jq '.active_sessions'

# watsonx connection
curl http://localhost:8000/api/test/watsonx
```

---

## 📚 Additional Resources

### Documentation
- [Setup Instructions](docs/SETUP_INSTRUCTIONS.md)
- [Data Flow](docs/DATA_FLOW.md)
- [Developer Guide](docs/README_DEVELOPER1.md)
- [Quick Start](docs/QUICKSTART.md)

### External Links
- [IBM watsonx.ai Documentation](https://www.ibm.com/docs/en/watsonx-as-a-service)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Zustand Documentation](https://zustand-demo.pmnd.rs/)

---

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

### Code Review Process
- All PRs require review
- Tests must pass
- Code must follow style guidelines
- Documentation must be updated

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👥 Team

Developed during IBM Bob Hackathon 2026

---

## 🙏 Acknowledgments

- IBM watsonx.ai team for AI platform
- Legal experts for domain knowledge
- Open source community for tools and libraries

---

## 📞 Support

For issues and questions:
- Create an issue on GitHub
- Check existing documentation
- Review troubleshooting guide

---

**Made with ❤️ for Indian Citizens**

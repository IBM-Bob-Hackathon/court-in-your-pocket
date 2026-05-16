from fastapi import FastAPI
from agents.classifier_agent import classify_issue
from agents.analysis_agent import analyze_rights
from routers.legal import router as legal_router

app = FastAPI()
app.include_router(legal_router)

@app.get("/")
def home():
    return {"status": "Court in Your Pocket API running"}

@app.get("/test-agents")
async def test_agents(language: str = "en"):
    """
    Test endpoint for agents with language support
    
    Query Parameters:
        language: Language code (en, hi, ta, te, kn, mr, bn). Default: en
    
    Examples:
        /test-agents (English - default)
        /test-agents?language=hi (Hindi)
        /test-agents?language=ta (Tamil)
        /test-agents?language=te (Telugu)
        /test-agents?language=kn (Kannada)
        /test-agents?language=mr (Marathi)
        /test-agents?language=bn (Bengali)
    """
    facts = {
        "issue": "landlord not returning security deposit",
        "location": "Bangalore",
        "amount": "4000",
        "dates": ["2026-03-15"],
        "partyName": "Mr. Sharma"
    }

    sample_law = [{
        "law_name": "Model Tenancy Act",
        "section": "Section 11",
        "plain_english": "Landlord must return deposit within 1 month",
        "exact_quote": "The landlord shall refund the security deposit...",
        "deadline_days": 90,
        "last_verified": "2026-01-01",
        "source_url": "https://indiacode.nic.in/..."
    }]

    classifier_result = await classify_issue(facts)
    analysis_result = await analyze_rights(facts, sample_law, language)

    return {
        "language": language,
        "classifier": classifier_result,
        "analysis": analysis_result
    }

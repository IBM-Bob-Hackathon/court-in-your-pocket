"""
Intake Agent — Production-grade, category-aware legal fact collection.

Acts like a lawyer: detects the type of legal issue first, then asks ONLY
the fields that are relevant and collectible for that issue type.
Never asks for information the user cannot possibly have (e.g. thief's name).
Ends every session with an open "anything else?" question.
"""

import os
import json
import re
import logging
from datetime import date, timedelta
from dotenv import load_dotenv

load_dotenv()

# Module-level constant for language mapping
LANGUAGE_MAP = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati"
}

logger = logging.getLogger(__name__)

WATSONX_API_KEY = os.getenv("IBM_WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("IBM_WATSONX_PROJECT_ID")
WATSONX_URL = os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")
WATSONX_ENABLED = bool(WATSONX_API_KEY and WATSONX_PROJECT_ID)

if WATSONX_ENABLED:
    try:
        from ibm_watsonx_ai.foundation_models import Model
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    except ImportError:
        WATSONX_ENABLED = False
        print("Warning: ibm-watsonx-ai not installed. Using rule-based fallback.")

# ── Category definitions ──────────────────────────────────────────────────────
# party_required = True  → ask for other party's name (they are known/identifiable)
# party_required = False → skip partyName (unknown perpetrator / not applicable)
# required_fields lists the MANDATORY fields for a complete intake in this category
# questions maps each field to the exact question to ask the user
# ─────────────────────────────────────────────────────────────────────────────

CATEGORIES = {
    "tenant": {
        "keywords": [
            "deposit", "security deposit", "rent", "landlord", "eviction",
            "tenant", "lease", "flat", "house", "pg", "paying guest", "room",
            "notice to vacate", "notice period rent"
        ],
        "party_required": True,
        "required_fields": ["issue", "location", "partyName", "amount", "dates"],
        "questions": {
            "issue":     "Can you describe the tenancy issue in more detail? (e.g. deposit not returned, illegal eviction)",
            "location":  "Which city is the property located in? This helps me apply the correct tenancy laws.",
            "partyName": "What is your landlord's full name?",
            "amount":    "What is the security deposit or rent amount involved? (in \u20b9)",
            "dates":     "When did you vacate the property, or when did this issue start?",
        },
    },
    "employment": {
        "keywords": [
            "salary", "wages", "employer", "fired", "termination", "job",
            "office", "workplac", "company", "bonus", "pf", "provident fund",
            "notice period", "dismissed", "layoff", "retrenchment", "hr"
        ],
        "party_required": True,
        "required_fields": ["issue", "location", "partyName", "amount", "dates"],
        "questions": {
            "issue":     "Can you describe the employment issue in more detail? (e.g. salary not paid, wrongful termination)",
            "location":  "Which city is your workplace located in?",
            "partyName": "What is the name of your employer or company?",
            "amount":    "What is the amount of unpaid salary or dues involved? (in \u20b9)",
            "dates":     "When did this happen? (e.g. date of termination, last date salary was paid)",
        },
    },
    "consumer": {
        "keywords": [
            "product", "defective", "refund", "online", "ecommerce", "purchase",
            "bought", "seller", "fraud", "cheated", "service", "delivery",
            "consumer", "warranty", "replacement", "damaged"
        ],
        "party_required": True,
        "required_fields": ["issue", "location", "partyName", "amount", "dates"],
        "questions": {
            "issue":     "Can you describe the consumer issue? (e.g. defective product, refund denied)",
            "location":  "Which city are you in?",
            "partyName": "What is the name of the seller, brand, or company involved?",
            "amount":    "What was the purchase amount or amount in dispute? (in \u20b9)",
            "dates":     "When did you make the purchase, or when did the issue occur?",
        },
    },
    "theft": {
        "keywords": [
            "theft", "stolen", "stole", "robbery", "robbed", "pickpocket",
            "burglary", "broke in", "broke into", "missing", "snatched",
            "thief", "chain snatching", "mugging", "looted", "loot",
            "lost", "lose", "lost my", "misplaced", "phone gone", "dropped"
        ],
        "party_required": False,   # perpetrator is typically unknown
        "required_fields": ["issue", "location", "amount", "dates"],
        "questions": {
            "issue":     "Can you describe what was stolen or what happened?",
            "location":  "Where did this happen? (city / area / specific place)",
            "amount":    "What is the approximate value of what was stolen? (in \u20b9)",
            "dates":     "When did this happen? Please share the date.",
        },
    },
    "harassment": {
        "keywords": [
            "harassment", "abuse", "domestic violence", "violence", "threat",
            "stalking", "assault", "dowry", "domestic", "mental harassment",
            "sexual harassment", "molestation"
        ],
        "party_required": False,   # victim may not want to name perpetrator early
        "required_fields": ["issue", "location", "dates"],
        "questions": {
            "issue":     "Can you describe what has been happening?",
            "location":  "Which city or state are you in?",
            "dates":     "When did this start, or when did the latest incident occur?",
        },
    },
    "property": {
        "keywords": [
            "property", "land", "plot", "encroachment", "boundary", "ownership",
            "title", "deed", "possession", "registry", "dispute", "neighbor"
        ],
        "party_required": True,
        "required_fields": ["issue", "location", "partyName", "dates"],
        "questions": {
            "issue":     "Can you describe the property dispute in more detail?",
            "location":  "Where is the disputed property located? (city / district)",
            "partyName": "Who is the other party in this dispute? (name of person or entity)",
            "dates":     "When did this dispute start?",
        },
    },
    "police_complaint": {
        "keywords": [
            "fir", "police", "complaint", "arrested", "custody", "bail",
            "chargesheet", "accused", "station"
        ],
        "party_required": False,
        "required_fields": ["issue", "location", "dates"],
        "questions": {
            "issue":     "Can you describe the situation involving the police?",
            "location":  "Which police station or city is this related to?",
            "dates":     "When did this happen?",
        },
    },
    "general": {
        "keywords": [],
        "party_required": False,
        "required_fields": ["issue", "location", "dates"],
        "questions": {
            "issue":     "Could you describe the legal issue you are facing in more detail?",
            "location":  "Which city are you in? This helps me apply the correct laws.",
            "dates":     "When did this happen? Please share the approximate date or time frame.",
        },
    },
}

# ── Helper functions ──────────────────────────────────────────────────────────

def detect_category(message: str) -> str:
    """Detect legal issue category from the user's first message."""
    msg_lower = message.lower()
    scores = {}
    for cat, data in CATEGORIES.items():
        if cat == "general":
            continue
        score = sum(1 for kw in data["keywords"] if kw in msg_lower)
        if score > 0:
            scores[cat] = score
    if scores:
        return max(scores, key=scores.get)
    return "general"


def get_required_fields(category: str) -> list:
    return list(CATEGORIES.get(category, CATEGORIES["general"])["required_fields"])


def get_question(category: str, field: str) -> str:
    q = CATEGORIES.get(category, CATEGORIES["general"]).get("questions", {}).get(field)
    fallback = {
        "issue":     "Could you describe the legal issue you are facing?",
        "location":  "Which city are you in?",
        "partyName": "What is the name of the other party involved?",
        "amount":    "Is there any money involved? If so, how much (in \u20b9)?",
        "dates":     "When did this happen? Please share the approximate date.",
    }
    return q or fallback.get(field, f"Could you tell me more about {field}?")


def field_missing(facts: dict, field: str) -> bool:
    v = facts.get(field)
    if field == "dates":
        return not v or len(v) == 0
    return not v


def extract_amount(message: str) -> str | None:
    """Extract ₹ amount from text."""
    patterns = [
        r'[\u20b9][\s]*(\d[\d,]*)',
        r'\brs\.?\s*(\d[\d,]*)',
        r'(\d[\d,]*)\s*(?:rupees?|lakh|lakhs?|thousand)',
        r'\b(\d[\d,]{2,})\b',   # bare number with 3+ digits
    ]
    for p in patterns:
        m = re.search(p, message, re.IGNORECASE)
        if m:
            return m.group(1).replace(',', '')
    return None


_MONTH_MAP = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
    "january": 1, "february": 2, "march": 3, "april": 4, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10,
    "november": 11, "december": 12,
}

_DAY_MAP = {
    "monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3,
    "friday": 4, "saturday": 5, "sunday": 6,
    "mon": 0, "tue": 1, "wed": 2, "thu": 3, "fri": 4, "sat": 5, "sun": 6,
}

def _to_ddmmyyyy(d: date) -> str:
    return d.strftime("%d/%m/%Y")


def _normalize_date_token(token: str) -> str | None:
    """
    Convert a single date token to dd/mm/yyyy.
    Handles:
      - dd/mm/yyyy, dd-mm-yyyy, mm/dd/yyyy variants
      - yyyy (year only)            → 01/01/yyyy
      - "Month yyyy" / "Month"      → 01/mm/yyyy
      - relative: yesterday, today, last week, last month, last year,
                  N days/weeks/months/years ago
    Returns None if unparseable.
    """
    today = date.today()
    t = token.strip().lower()

    # ── Relative keywords ──────────────────────────────────────────────────
    if t == "today":
        return _to_ddmmyyyy(today)
    if t in ("yesterday", "last day"):
        return _to_ddmmyyyy(today - timedelta(days=1))
    if t in ("last week", "previous week"):
        return _to_ddmmyyyy(today - timedelta(weeks=1))
    if t in ("last month", "previous month"):
        d = today.replace(day=1)
        d = (d - timedelta(days=1)).replace(day=1)
        return _to_ddmmyyyy(d)
    if t in ("last year", "previous year"):
        return _to_ddmmyyyy(today.replace(year=today.year - 1, day=1, month=1))

    # ── "last <weekday>" or "last week <weekday>" ─────────────────────────
    m = re.match(r'^(?:last\s+week\s+|last\s+)(monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun)$', t)
    if m:
        target_wd = _DAY_MAP[m.group(1)]
        days_ago = (today.weekday() - target_wd) % 7
        if days_ago == 0:
            days_ago = 7   # "last wednesday" when today IS wednesday → previous wednesday
        return _to_ddmmyyyy(today - timedelta(days=days_ago))

    # ── "N unit(s) ago" ───────────────────────────────────────────────────
    m = re.match(r'^(\d+)\s*(day|week|month|year)s?\s*ago$', t)
    if m:
        n, unit = int(m.group(1)), m.group(2)
        if unit == "day":
            return _to_ddmmyyyy(today - timedelta(days=n))
        if unit == "week":
            return _to_ddmmyyyy(today - timedelta(weeks=n))
        if unit == "month":
            month = today.month - n
            year = today.year + (month - 1) // 12
            month = ((month - 1) % 12) + 1
            return _to_ddmmyyyy(today.replace(year=year, month=month, day=1))
        if unit == "year":
            return _to_ddmmyyyy(today.replace(year=today.year - n, day=1, month=1))

    # ── dd/mm/yyyy or dd-mm-yyyy ──────────────────────────────────────────
    m = re.match(r'^(\d{1,2})[\/\-](\d{1,2})[\/\-](\d{2,4})$', t)
    if m:
        p1, p2, p3 = int(m.group(1)), int(m.group(2)), int(m.group(3))
        yr = p3 + 2000 if p3 < 100 else p3
        # Prefer dd/mm — if p1 > 12 it must be day; otherwise day-first (Indian convention)
        day, mon = (p1, p2) if p1 > 12 else (p1, p2)
        try:
            return _to_ddmmyyyy(date(yr, mon, day))
        except ValueError:
            pass

    # ── yyyy only ─────────────────────────────────────────────────────────
    m = re.match(r'^(\d{4})$', t)
    if m:
        yr = int(m.group(1))
        if 1900 < yr <= today.year:
            return f"01/01/{yr}"

    # ── "Month yyyy" or "Month" only ──────────────────────────────────────
    m = re.match(r'^([a-z]+)\.?\s*(\d{4})?$', t)
    if m:
        mon_str = m.group(1)[:3]
        yr_str = m.group(2)
        mon = _MONTH_MAP.get(mon_str)
        if mon:
            yr = int(yr_str) if yr_str else today.year
            return f"01/{mon:02d}/{yr}"

    return None


def extract_dates(message: str) -> list:
    """
    Extract and normalize all date/time references from user text to dd/mm/yyyy.
    Handles relative references (yesterday, 2 months ago, last year),
    partial dates (May 2024, 2023), and exact dates (12/05/2024).
    """
    today = date.today()
    raw_patterns = [
        # dd/mm/yyyy or dd-mm-yyyy  (most specific first)
        r'\b(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})\b',
        # N days/weeks/months/years ago
        r'\b(\d+\s*(?:day|week|month|year)s?\s+ago)\b',
        # "last week <weekday>"  — MUST be before "last week" so longer match wins
        r'\b(last\s+week\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun))\b',
        # "last <weekday>"       — MUST be before "last <unit>"
        r'\b(last\s+(?:monday|tuesday|wednesday|thursday|friday|saturday|sunday|mon|tue|wed|thu|fri|sat|sun))\b',
        # last/previous + unit
        r'\b(last\s+(?:day|week|month|year)|yesterday|today|previous\s+(?:week|month|year))\b',
        # Month + optional year
        r'\b((?:january|february|march|april|may|june|july|august|september|october|november|december|'
        r'jan|feb|mar|apr|jun|jul|aug|sep|oct|nov|dec)\.?\s*\d{0,4})\b',
        # bare 4-digit year
        r'\b(\d{4})\b',
    ]
    raw_tokens = []
    # Process patterns in order of specificity — skip year-only if a fuller date was already matched
    matched_spans = []
    for p in raw_patterns:
        for m in re.finditer(p, message, re.IGNORECASE):
            # Skip if this span is already covered by a longer/earlier match
            start, end = m.start(1), m.end(1)
            if any(s <= start and end <= e for s, e in matched_spans):
                continue
            val = m.group(1).strip()
            if val and val.lower() not in [x.lower() for x in raw_tokens]:
                raw_tokens.append(val)
                matched_spans.append((start, end))

    normalized = []
    seen = set()
    for tok in raw_tokens:
        nd = _normalize_date_token(tok)
        if nd and nd not in seen:
            seen.add(nd)
            normalized.append(nd)
        elif not nd and tok not in seen:
            # Keep original if we can't normalize (don't lose info)
            seen.add(tok)
            normalized.append(tok)

    return normalized


def light_regex_pass(message: str, facts: dict) -> dict:
    """
    Run lightweight, safe regex on every message to catch obvious facts.
    Only sets a field if it's still empty — never overwrites.
    Does NOT attempt to extract partyName via sentence patterns (too error-prone).
    """
    facts = dict(facts)
    msg_lower = message.lower()

    # Issue keywords
    issue_map = {
        "deposit":     "security deposit not returned",
        "salary":      "salary not paid",
        "wages":       "wages not paid",
        "defective":   "defective product",
        "fraud":       "consumer fraud",
        "termination": "wrongful termination",
        "eviction":    "illegal eviction",
        "theft":       "theft / robbery",
        "stolen":      "theft / robbery",
    }
    if field_missing(facts, "issue"):
        for kw, issue in issue_map.items():
            if kw in msg_lower:
                facts["issue"] = issue
                break

    # Location — Indian cities only
    cities = [
        "bangalore", "bengaluru", "mumbai", "delhi", "pune", "hyderabad",
        "chennai", "kolkata", "ahmedabad", "jaipur", "lucknow", "surat",
        "kanpur", "nagpur", "indore", "bhopal", "patna", "vadodara",
        "coimbatore", "kochi", "noida", "gurugram", "gurgaon", "faridabad",
    ]
    if field_missing(facts, "location"):
        for city in cities:
            if city in msg_lower:
                facts["location"] = city.replace("bengaluru", "Bangalore").title()
                break

    # Amount
    if field_missing(facts, "amount"):
        amt = extract_amount(message)
        if amt:
            facts["amount"] = amt

    # Dates
    if field_missing(facts, "dates"):
        dates = extract_dates(message)
        if dates:
            facts["dates"] = dates

    # partyName — ONLY via honorific prefix (Mr./Mrs./Dr./Shri/Smt.)
    # Never use sentence patterns — they cause false positives.
    if field_missing(facts, "partyName"):
        m = re.search(
            r'\b(?:mr\.?|mrs\.?|ms\.?|dr\.?|shri\.?|smt\.?)\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)',
            message, re.IGNORECASE
        )
        if m:
            facts["partyName"] = m.group(1).strip().title()

    return facts


def detect_pending_field(last_bob_message: str, facts: dict, required_fields: list) -> str | None:
    """
    Given Bob's last question, identify which field he was asking for.
    Uses keyword signals specific to each field.
    """
    SIGNALS = {
        "issue":     ["describe", "legal issue", "facing", "problem", "happened", "situation"],
        "location":  ["city", "located", "where", "area", "district", "state"],
        "partyName": ["landlord", "employer", "company", "seller", "other party",
                      "name of", "full name", "who is", "brand", "entity"],
        "amount":    ["amount", "money", "rupees", "\u20b9", "rs.", "paid", "value", "worth"],
        "dates":     ["when", "date", "vacate", "happen", "start", "termination",
                      "purchase", "incident", "occur"],
    }
    for field in required_fields:
        if not field_missing(facts, field):
            continue   # already filled — not what Bob was asking
        sigs = SIGNALS.get(field, [])
        if any(s in last_bob_message for s in sigs):
            return field
    return None


# ── IBM watsonx path ──────────────────────────────────────────────────────────

def get_bob_model():
    if not WATSONX_ENABLED:
        return None
    try:
        model = Model(
            model_id="meta-llama/llama-3-3-70b-instruct",
            params={
                GenParams.DECODING_METHOD: "greedy",
                GenParams.MAX_NEW_TOKENS: 400,
                GenParams.MIN_NEW_TOKENS: 20,
                GenParams.TEMPERATURE: 0.3,
                GenParams.TOP_K: 50,
                GenParams.TOP_P: 1,
            },
            credentials={"apikey": WATSONX_API_KEY, "url": WATSONX_URL},
            project_id=WATSONX_PROJECT_ID,
        )
        return model
    except Exception as e:
        print(f"Error initializing watsonx model: {e}")
        return None


def build_watsonx_prompt(session: dict, user_message: str, formatted_history: str,
                          category: str, required_fields: list, facts: dict) -> str:
    language_code = session.get('language', 'en')
    if language_code not in LANGUAGE_MAP:
        logger.warning(f"Unsupported language code: {language_code}, defaulting to English")
    lang_name = LANGUAGE_MAP.get(language_code, 'English')
    party_note = (
        "partyName IS required — ask for it when missing."
        if "partyName" in required_fields
        else "⚠️ partyName is NOT required for this category. NEVER ask for it under any circumstances."
    )
    missing = [f for f in required_fields if field_missing(facts, f)]
    extra_info_asked = facts.get("extraInfoAsked", False)

    return f"""You are a professional legal intake specialist for "Court in Your Pocket", an AI-powered legal assistant for Indians.

ISSUE CATEGORY: {category}
{party_note}

ONLY THESE FIELDS ARE REQUIRED: {required_fields}
STILL MISSING: {missing}
FACTS COLLECTED SO FAR: {json.dumps({k: v for k, v in facts.items() if v and k != 'extraInfoAsked'}, ensure_ascii=False)}

STRICT RULES:
1. ONLY collect the fields listed in REQUIRED FIELDS above. Do NOT ask for anything else.
2. Ask ONE question at a time about the NEXT missing field from the STILL MISSING list.
3. Be empathetic and professional.
4. For dates: record exactly what the user says (e.g. "yesterday", "last week", "12/05/2024").
5. If STILL MISSING is empty and extraInfoAsked is false, ask: "Is there anything else you would like to share that might be relevant?"
6. If extraInfoAsked is true OR user replies no to the above, set readyForAnalysis to true.
7. YOU MUST respond ONLY in {lang_name}. This is mandatory.
8. Extract multiple facts from one message when possible.

SESSION: language={session.get('language','en')} ({lang_name}), state={session.get('state','KA')}
EXTRA INFO ALREADY ASKED: {extra_info_asked}

{formatted_history}

USER: {user_message}

Respond ONLY with valid JSON (no extra text before or after):
{{
  "reply": "your next question or acknowledgment",
  "extractedFacts": {{...updated facts with all collected values...}},
  "readyForAnalysis": false,
  "category": "{category}"
}}"""


# ── Main entry point ──────────────────────────────────────────────────────────

async def process_intake(session: dict, user_message: str, formatted_history: str = "") -> dict:
    """
    Production-grade intake agent.
    Detects issue category, collects only relevant mandatory fields,
    and ends with an open 'anything else?' question before handing off.
    """

    # ── 1. Bootstrap facts ────────────────────────────────────────────────────
    facts = dict(session.get("extractedFacts", {}))
    for key in ["issue", "location", "partyName", "amount", "dates", "additionalInfo"]:
        if key not in facts:
            facts[key] = [] if key == "dates" else None
    # extraInfoAsked is a control flag, not a real fact
    extra_info_asked = facts.pop("extraInfoAsked", False)

    # ── 2. Detect / confirm category ─────────────────────────────────────────
    category = session.get("category") or detect_category(user_message)
    session["category"] = category
    required_fields = get_required_fields(category)

    # ── 3. Try IBM Bob ────────────────────────────────────────────────────────
    if WATSONX_ENABLED:
        try:
            model = get_bob_model()
            if model:
                prompt = build_watsonx_prompt(
                    session, user_message, formatted_history,
                    category, required_fields, {**facts, "extraInfoAsked": extra_info_asked}
                )
                raw = model.generate_text(prompt=prompt)
                try:
                    m = re.search(r'\{.*\}', raw, re.DOTALL)
                    if m:
                        resp = json.loads(m.group())
                        merged = {**facts, **resp.get("extractedFacts", {})}
                        # Normalize any raw date strings IBM returned (e.g. "yesterday" → "16/05/2026")
                        if merged.get("dates"):
                            normed = []
                            for d in merged["dates"]:
                                d_str = str(d).strip()
                                if re.match(r'^\d{2}/\d{2}/\d{4}$', d_str):
                                    normed.append(d_str)  # already normalized
                                else:
                                    nd = _normalize_date_token(d_str.lower())
                                    normed.append(nd if nd else d_str)
                            merged["dates"] = list(dict.fromkeys(normed))  # deduplicate
                        resp["extractedFacts"] = merged
                        resp.setdefault("chips", [])
                        return resp
                except (json.JSONDecodeError, ValueError):
                    print(f"IBM Bob JSON parse failed: {raw[:200]}")
        except Exception as e:
            print(f"IBM Bob error: {e}")

    # ── 4. Rule-based fallback ────────────────────────────────────────────────

    # 4a. Run safe regex on the current message (catches cities, amounts, dates, honorifics)
    facts = light_regex_pass(user_message, facts)

    # 4b. Identify which field Bob was asking for in his last message
    history = session.get("conversationHistory", [])
    last_bob = ""
    for msg in reversed(history):
        if msg.get("role") == "assistant":
            last_bob = msg.get("content", "").lower()
            break

    pending = detect_pending_field(last_bob, facts, required_fields)
    cleaned = user_message.strip().rstrip(".,!?")

    # 4c. Directly assign the user's reply to the pending field (regex-bypasses for plain answers)
    if pending and field_missing(facts, pending):
        if pending == "issue":
            facts["issue"] = cleaned

        elif pending == "location":
            facts["location"] = cleaned.title()

        elif pending == "partyName":
            facts["partyName"] = cleaned.title()

        elif pending == "amount":
            amt = extract_amount(user_message) or cleaned
            facts["amount"] = amt

        elif pending == "dates":
            extracted = extract_dates(user_message)
            facts["dates"] = extracted if extracted else [cleaned]

    # 4d. If the extra-info question was asked, capture the reply as additionalInfo
    if extra_info_asked and "anything else" in last_bob:
        lower = cleaned.lower()
        no_answers = ["no", "nothing", "nope", "that's all", "thats all",
                      "nothing else", "no that's all", "i think that's all"]
        if not any(a in lower for a in no_answers):
            facts["additionalInfo"] = cleaned
        # Either way — we're done
        facts["extraInfoAsked"] = True
        return {
            "reply": "Thank you. I now have all the information needed to analyze your legal situation.",
            "extractedFacts": facts,
            "chips": [],
            "readyForAnalysis": True,
            "category": category,
        }

    # 4e. Check each required field in order
    is_emotional = any(w in user_message.lower() for w in [
        "stressed", "worried", "scared", "helpless", "frustrated",
        "please help", "desperate", "crying", "don't know"
    ])
    empathy = "I understand this must be stressful. " if is_emotional else ""

    for field in required_fields:
        if field_missing(facts, field):
            q = get_question(category, field)
            return {
                "reply": f"{empathy}{q}" if empathy else q,
                "extractedFacts": facts,
                "chips": [],
                "readyForAnalysis": False,
                "category": category,
            }

    # 4f. All required fields filled — ask the open "anything else?" question
    if not extra_info_asked:
        facts["extraInfoAsked"] = True
        return {
            "reply": (
                "Thank you for sharing all the details. Before I analyze your case, "
                "is there anything else you would like to share? "
                "(Any witnesses, documents, prior complaints, or other relevant details)"
            ),
            "extractedFacts": facts,
            "chips": ["No, that's all", "Yes, I have more"],
            "readyForAnalysis": False,
            "category": category,
        }

    # Fallback — should not reach here
    facts["extraInfoAsked"] = True
    return {
        "reply": "Thank you. I now have everything I need.",
        "extractedFacts": facts,
        "chips": [],
        "readyForAnalysis": True,
        "category": category,
    }


async def test_bob():
    """Test IBM Bob connection"""
    if not WATSONX_ENABLED:
        print("IBM watsonx not configured.")
        return
    model = get_bob_model()
    if not model:
        print("Failed to init model.")
        return
    try:
        r = model.generate_text(prompt="Say hello in one sentence.")
        print(f"Bob says: {r}")
    except Exception as e:
        print(f"Error: {e}")


# Load environment variables
load_dotenv()

# IBM watsonx configuration
WATSONX_API_KEY = os.getenv("IBM_WATSONX_API_KEY")
WATSONX_PROJECT_ID = os.getenv("IBM_WATSONX_PROJECT_ID")
WATSONX_URL = os.getenv("IBM_WATSONX_URL", "https://us-south.ml.cloud.ibm.com")

# Check if watsonx is configured
WATSONX_ENABLED = bool(WATSONX_API_KEY and WATSONX_PROJECT_ID)

if WATSONX_ENABLED:
    try:
        from ibm_watsonx_ai.foundation_models import Model
        from ibm_watsonx_ai.metanames import GenTextParamsMetaNames as GenParams
    except ImportError:
        WATSONX_ENABLED = False
        print("Warning: ibm-watsonx-ai not installed. Using fallback mode.")

INTAKE_SYSTEM_PROMPT = """You are a legal intake assistant for "Court in Your Pocket", an AI legal companion for Indians who cannot afford lawyers.

Your role:
1. Extract facts from the user's description of their legal issue
2. Ask ONE clarifying question at a time
3. Be empathetic but professional
4. Do NOT give legal advice yet - just gather information
5. Respond ONLY in the language specified in the session (English, Hindi, Tamil, Telugu, Kannada, Marathi, Bengali, or Gujarati)

Facts to extract — you MUST collect ALL of these before setting readyForAnalysis to true:
- issue: What is the legal problem? (e.g., "security deposit not returned", "salary not paid", "defective product")
- location: Which city/state? (needed to apply correct laws)
- partyName: Who is the other party? (landlord name, employer name, company name)
- amount: Any money involved? (in ₹ — ask even if user hasn't mentioned it)
- dates: When did this happen? (move-out date, termination date, purchase date, etc.)

Rules:
- Collect facts in this order: issue → location → partyName → amount → dates
- Ask about the next missing fact — do NOT skip any
- Only set readyForAnalysis to true when ALL 5 fields above are filled
- Keep questions simple and conversational
- If user is emotional, acknowledge their feelings first
- Extract multiple facts from a single message if provided

Return your response as JSON:
{
  "reply": "Your next question or acknowledgment",
  "extractedFacts": {
    "issue": "...",
    "location": "...",
    "partyName": "...",
    "amount": "...",
    "dates": ["..."]
  },
  "chips": [],
  "readyForAnalysis": false
}

Examples:

Example 1 - First message:
User: "My landlord is not returning my deposit"
You: {
  "reply": "I'm sorry to hear that. Which city are you in? This helps me find the right laws for your area.",
  "extractedFacts": {"issue": "security deposit not returned", "location": null, "partyName": null, "amount": null, "dates": []},
  "chips": [],
  "readyForAnalysis": false
}

Example 2 - Location provided:
User: "Bangalore"
You: {
  "reply": "Got it. What is your landlord's name?",
  "extractedFacts": {"issue": "security deposit not returned", "location": "Bangalore", "partyName": null, "amount": null, "dates": []},
  "chips": [],
  "readyForAnalysis": false
}

Example 3 - partyName provided:
User: "Mr. Sharma"
You: {
  "reply": "Thank you. How much was the security deposit amount (in ₹)?",
  "extractedFacts": {"issue": "security deposit not returned", "location": "Bangalore", "partyName": "Mr. Sharma", "amount": null, "dates": []},
  "chips": [],
  "readyForAnalysis": false
}

Example 4 - Amount provided:
User: "50000 rupees"
You: {
  "reply": "When did you move out? Please share the approximate date.",
  "extractedFacts": {"issue": "security deposit not returned", "location": "Bangalore", "partyName": "Mr. Sharma", "amount": "50000", "dates": []},
  "chips": [],
  "readyForAnalysis": false
}

Example 5 - All facts collected:
User: "I moved out 2 months ago, around March 2026."
You: {
  "reply": "Thank you for providing all the details. I now have everything I need to analyze your situation.",
  "extractedFacts": {"issue": "security deposit not returned", "location": "Bangalore", "partyName": "Mr. Sharma", "amount": "50000", "dates": ["March 2026"]},
  "chips": [],
  "readyForAnalysis": true
}

Now process the actual conversation below."""


def get_bob_model():
    """Initialize IBM watsonx model for intake agent"""
    if not WATSONX_ENABLED:
        return None
    
    try:
        model = Model(
            model_id="meta-llama/llama-3-3-70b-instruct",
            params={
                GenParams.DECODING_METHOD: "greedy",
                GenParams.MAX_NEW_TOKENS: 300,
                GenParams.MIN_NEW_TOKENS: 50,
                GenParams.TEMPERATURE: 0.7,
                GenParams.TOP_K: 50,
                GenParams.TOP_P: 1
            },
            credentials={
                "apikey": WATSONX_API_KEY,
                "url": WATSONX_URL
            },
            project_id=WATSONX_PROJECT_ID
        )
        return model
    except Exception as e:
        print(f"Error initializing watsonx model: {e}")
        return None


def extract_facts_with_regex(message: str, current_facts: dict) -> dict:
    """
    Fallback fact extraction using regex patterns
    Used when IBM Bob is not available
    """
    facts = current_facts.copy()
    message_lower = message.lower()
    
    # Extract location (Indian cities)
    cities = ["bangalore", "bengaluru", "mumbai", "delhi", "pune", "hyderabad",
              "chennai", "kolkata", "ahmedabad", "jaipur", "lucknow", "kanpur"]
    for city in cities:
        if city in message_lower:
            facts["location"] = city.capitalize()
            if city == "bengaluru":
                facts["location"] = "Bangalore"
            break
    
    # Extract amount
    amount_patterns = [
        r'₹\s*(\d+(?:,\d+)*)',
        r'rs\.?\s*(\d+(?:,\d+)*)',
        r'rupees?\s*(\d+(?:,\d+)*)',
        r'(\d+(?:,\d+)*)\s*rupees?'
    ]
    for pattern in amount_patterns:
        match = re.search(pattern, message_lower)
        if match:
            facts["amount"] = match.group(1).replace(',', '')
            break
    
    # Extract dates
    date_patterns = [
        r'(\d+)\s+(?:months?|weeks?|days?)\s+ago',
        r'(?:on|in)\s+(\w+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s+\d{4})?)'
    ]
    dates = facts.get("dates", [])
    for pattern in date_patterns:
        matches = re.findall(pattern, message_lower)
        dates.extend(matches)
    if dates:
        facts["dates"] = list(set(dates))  # Remove duplicates
    
    # Extract issue keywords
    issue_keywords = {
        "deposit": "security deposit not returned",
        "salary": "salary not paid",
        "wages": "wages not paid",
        "defective": "defective product",
        "fraud": "consumer fraud",
        "termination": "wrongful termination",
        "eviction": "illegal eviction"
    }
    if not facts.get("issue"):
        for keyword, issue in issue_keywords.items():
            if keyword in message_lower:
                facts["issue"] = issue
                break

    # Extract partyName — ONLY via honorific prefix (Mr./Mrs./Dr. etc.)
    # Do NOT try to extract from phrases like "landlord is X" — too error-prone
    if not facts.get("partyName"):
        honorific_pattern = r'\b(?:mr\.?|mrs\.?|ms\.?|dr\.?|shri\.?|smt\.?)\s+([A-Za-z]+(?:\s+[A-Za-z]+)*)'
        match = re.search(honorific_pattern, message, re.IGNORECASE)
        if match:
            facts["partyName"] = match.group(1).strip().title()

    return facts


def detect_emotional_language(message: str) -> bool:
    """Check if user is distressed"""
    emotional_keywords = [
        "stressed", "worried", "scared", "helpless", "frustrated",
        "angry", "upset", "desperate", "confused", "don't know what to do"
    ]
    return any(keyword in message.lower() for keyword in emotional_keywords)


async def process_intake(session: dict, user_message: str, formatted_history: str = "") -> dict:
    """
    Process user message during intake stage.
    Uses IBM watsonx if available, falls back to a strict state-machine extractor.
    """
    extracted_facts = session.get("extractedFacts", {
        "issue": None,
        "location": None,
        "partyName": None,
        "amount": None,
        "dates": []
    })
    # Ensure all keys exist
    for key in ["issue", "location", "partyName", "amount", "dates"]:
        if key not in extracted_facts:
            extracted_facts[key] = [] if key == "dates" else None

    # Try IBM Bob first
    if WATSONX_ENABLED:
        try:
            model = get_bob_model()
            if model:
                language_code = session.get('language', 'en')
                if language_code not in LANGUAGE_MAP:
                    logger.warning(f"Unsupported language code: {language_code}, defaulting to English")
                lang_name = LANGUAGE_MAP.get(language_code, 'English')
                prompt = f"""{INTAKE_SYSTEM_PROMPT}

=== Current Session ===
Language: {session.get('language', 'en')} ({lang_name})
IMPORTANT: You MUST write your "reply" field ONLY in {lang_name}. No other language is acceptable.
State: {session.get('state', 'KA')}

{formatted_history}

=== User's Latest Message ===
{user_message}

=== Your Task ===
1. Update extractedFacts based on the user's message
2. Follow this exact collection order: issue → location → partyName → amount → dates
3. Ask ONE clarifying question about the next missing field in that order
4. Only set readyForAnalysis to true when ALL 5 fields (issue, location, partyName, amount, dates) are filled

Respond ONLY with valid JSON. No other text."""

                response_text = model.generate_text(prompt=prompt)
                try:
                    json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                    if json_match:
                        response = json.loads(json_match.group())
                        merged_facts = {**extracted_facts, **response.get("extractedFacts", {})}
                        response["extractedFacts"] = merged_facts
                        return response
                except json.JSONDecodeError:
                    print(f"Failed to parse Bob's response as JSON: {response_text}")
        except Exception as e:
            print(f"Error calling IBM Bob: {e}")

    # ── Fallback: strict state-machine extractor ──────────────────────────────
    # Run regex first to catch obvious facts (cities, amounts, dates, issue keywords)
    # Direct assignment below will override for the specific pending field.
    extracted_facts = extract_facts_with_regex(user_message, extracted_facts)

    # Determine which field Bob asked for in his LAST message.
    # The user's current reply is the direct answer to that field.
    history = session.get("conversationHistory", [])
    last_bob_message = ""
    for msg in reversed(history):
        if msg.get("role") == "assistant":
            last_bob_message = msg.get("content", "").lower()
            break

    PENDING_FIELD_SIGNALS = {
        "issue":     ["legal issue", "problem", "facing", "describe"],
        "location":  ["city", "which city", "location", "area", "state"],
        "partyName": ["name of the other party", "landlord", "employer", "company", "other party"],
        "amount":    ["money", "amount", "how much", "rupees", "₹"],
        "dates":     ["when did", "date", "happen", "how long", "approximate"],
    }

    # Find which field Bob was asking about in his last message
    pending_field = None
    for field, signals in PENDING_FIELD_SIGNALS.items():
        if any(signal in last_bob_message for signal in signals):
            if field == "dates":
                if not extracted_facts.get("dates"):
                    pending_field = field
                    break
            else:
                if not extracted_facts.get(field):
                    pending_field = field
                    break

    # Directly assign the user's reply to the pending field
    cleaned_reply = user_message.strip().rstrip(".,!?")

    if pending_field == "issue" and not extracted_facts.get("issue"):
        extracted_facts["issue"] = cleaned_reply

    elif pending_field == "location" and not extracted_facts.get("location"):
        extracted_facts["location"] = cleaned_reply.title()

    elif pending_field == "partyName" and not extracted_facts.get("partyName"):
        extracted_facts["partyName"] = cleaned_reply.title()

    elif pending_field == "amount" and not extracted_facts.get("amount"):
        # Accept bare number or ₹-prefixed
        num = re.search(r'[\d,]+', user_message.replace(',', ''))
        extracted_facts["amount"] = num.group().replace(',', '') if num else cleaned_reply

    elif pending_field == "dates" and not (extracted_facts.get("dates") and len(extracted_facts["dates"]) > 0):
        extracted_facts["dates"] = [cleaned_reply]

    # ── Determine next question ───────────────────────────────────────────────
    is_emotional = detect_emotional_language(user_message)
    empathy_prefix = "I understand this is a difficult situation. " if is_emotional else ""

    MANDATORY_FIELDS = ["issue", "location", "partyName", "amount", "dates"]

    def field_missing(f):
        v = extracted_facts.get(f)
        if f == "dates":
            return not v or len(v) == 0
        return not v

    QUESTIONS = {
        "issue":     f"{empathy_prefix}Could you briefly describe the legal issue you are facing?",
        "location":  "Which city are you in? This helps me apply the correct laws.",
        "partyName": "What is the name of the other party — the landlord, employer, or company involved?",
        "amount":    "Is there any money involved in this matter? If so, how much (in \u20b9)?",
        "dates":     "When did this happen? Please share the approximate date or time frame.",
    }

    for field in MANDATORY_FIELDS:
        if field_missing(field):
            return {
                "reply": QUESTIONS[field],
                "extractedFacts": extracted_facts,
                "chips": [],
                "readyForAnalysis": False
            }

    # All 5 facts collected
    return {
        "reply": "Thank you for sharing all the details. I now have everything I need to analyze your legal situation.",
        "extractedFacts": extracted_facts,
        "chips": [],
        "readyForAnalysis": True
    }


async def test_bob():
    """Test function to verify IBM Bob connection"""
    if not WATSONX_ENABLED:
        print("IBM watsonx is not configured. Set WATSONX_API_KEY and WATSONX_PROJECT_ID in .env file.")
        return
    
    model = get_bob_model()
    if not model:
        print("Failed to initialize IBM Bob model")
        return
    
    prompt = "You are a helpful legal assistant. Say hello in one sentence."
    
    try:
        response = model.generate_text(prompt=prompt)
        print(f"Bob says: {response}")
        return response
    except Exception as e:
        print(f"Error testing Bob: {e}")
        return None

# Made with Bob

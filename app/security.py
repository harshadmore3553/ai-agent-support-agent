import re

PROMPT_EXTRACTION_PATTERNS = [
    r"system prompt",
    r"hidden instructions",
    r"developer instructions",
    r"reveal.*prompt",
    r"show.*secret",
    r"ignore.*previous.*instructions",
]

SENSITIVE_PATTERNS = [
    r"\bemail\b",
    r"\baddress\b",
    r"\binternal note\b",
    r"\brisk score\b",
    r"\bfraud review\b",
]

def is_prompt_extraction(text: str) -> bool:
    return any(re.search(p, text, re.I) for p in PROMPT_EXTRACTION_PATTERNS)

def is_sensitive_request(text: str) -> bool:
    return any(re.search(p, text, re.I) for p in SENSITIVE_PATTERNS)

def contains_order_id(text: str) -> str | None:
    match = re.search(r"\bORD-\d+\b", text, re.I)
    return match.group(0).upper() if match else None

def looks_like_order_question(text: str) -> bool:
    lower = text.lower()
    order_terms = ("order", "tracking", "shipment", "arrive", "delivery", "where is")
    return bool(contains_order_id(text)) and any(term in lower for term in order_terms)

def looks_like_action_request(text: str) -> bool:
    return bool(re.search(r"\b(cancel|refund|replace|change (my )?address|approve)\b", text, re.I))

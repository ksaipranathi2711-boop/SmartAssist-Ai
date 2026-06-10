"""Rule-based intent classifier. Returns one of:
greeting, farewell, refund, order_status, password_reset, pricing,
contact_human, hours, thanks, complaint, faq, unknown."""
import re
PATTERNS = [
    ("greeting", r"\b(hi|hello|hey|good (morning|evening|afternoon))\b"),
    ("farewell", r"\b(bye|goodbye|see you|cya)\b"),
    ("thanks",   r"\b(thanks|thank you|thx|appreciate)\b"),
    ("refund",   r"\b(refund|money back|return)\b"),
    ("order_status", r"\b(order|track|shipment|delivery|where is)\b"),
    ("password_reset", r"\b(password|forgot|reset|login issue)\b"),
    ("pricing",  r"\b(price|cost|pricing|plan|subscription)\b"),
    ("contact_human", r"\b(human|agent|representative|talk to (someone|a person))\b"),
    ("hours",    r"\b(hours|open|available|when.*open)\b"),
    ("complaint",r"\b(angry|bad|terrible|worst|complain|complaint|hate)\b"),
]
def classify_intent(text:str)->str:
    t = text.lower()
    for name, pat in PATTERNS:
        if re.search(pat, t): return name
    return "faq"

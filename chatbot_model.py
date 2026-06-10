"""Generate replies based on intent + FAQ lookup."""
import re
RESPONSES = {
    "greeting": "Hello! I'm SmartAssist AI. How can I help you today?",
    "farewell": "Goodbye! Have a great day.",
    "thanks":   "You're welcome! Anything else I can help with?",
    "refund":   "Refunds are available within 30 days. Share your order ID and I'll start the process.",
    "order_status": "Please share your order ID and I'll look up the latest status for you.",
    "password_reset": "To reset your password, go to Settings > Security > Reset Password.",
    "pricing":  "Our plans start at $9/month. Visit the Pricing page for full details.",
    "contact_human": "I'm creating a support ticket — a human agent will reach out within 24 hours.",
    "hours":    "Our support team is available 24/7 via chat.",
    "complaint":"I'm sorry to hear that. Could you share more details so I can help resolve it?",
}
def _faq_lookup(message, db_factory):
    conn = db_factory()
    rows = conn.execute("SELECT question, answer FROM faqs").fetchall()
    conn.close()
    msg_words = set(re.findall(r"\w+", message.lower()))
    best, score = None, 0
    for r in rows:
        qw = set(re.findall(r"\w+", r["question"].lower()))
        s = len(msg_words & qw)
        if s > score:
            best, score = r, s
    if best and score >= 2:
        return best["answer"]
    return None
def get_bot_reply(message, intent, db_factory):
    if intent in RESPONSES:
        return RESPONSES[intent]
    ans = _faq_lookup(message, db_factory)
    if ans: return ans
    return "I'm not sure I understood. Could you rephrase, or create a ticket for human support?"

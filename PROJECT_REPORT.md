# SmartAssist AI – Project Report

## Objective
Build a production-ready AI-powered customer service chatbot for internship submission.

## Modules
1. Authentication (Werkzeug hashed passwords, session-based)
2. Chatbot engine (intent classification + FAQ lookup + sentiment)
3. Analytics (intent/sentiment distribution, daily volume)
4. FAQ manager
5. Ticket system

## AI Components
- **Intent classifier**: regex pattern matching across 11 intents.
- **Sentiment analyzer**: lexicon-based scoring (positive/neutral/negative).
- **Reply generator**: rule-based with FAQ fallback (word-overlap scoring).

## Database (SQLite)
Tables: `users`, `chats`, `faqs`, `tickets`.

## How to Extend
- Swap regex classifier for scikit-learn `TfidfVectorizer + LogisticRegression`.
- Swap lexicon sentiment for `TextBlob` or HuggingFace transformer.
- Add OpenAI/Gemini API call inside `models/chatbot_model.py`.

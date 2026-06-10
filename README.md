# SmartAssist AI — Customer Service Chatbot

A Flask-based AI customer service chatbot with authentication, analytics, FAQ management, and ticket support.

## Features
- 🔐 Username/password authentication (default: `admin` / `admin123`)
- 💬 AI chatbot with intent classification + sentiment analysis
- 📊 Analytics dashboard (Chart.js): intents, sentiment, daily volume
- ❓ FAQ management (add/delete)
- 🎫 Support ticket system
- 📱 Fully responsive dark UI

## Quick Start
```bash
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000 and log in with `admin` / `admin123`.

## Project Structure
```
SmartAssistAI/
├── app.py                  # Flask app and routes
├── requirements.txt
├── README.md
├── models/
│   ├── chatbot_model.py    # Reply generation
│   ├── sentiment_model.py  # Lexicon sentiment
│   └── intent_classifier.py# Regex intent classifier
├── templates/              # Jinja2 HTML
├── static/css/style.css
├── static/js/app.js
├── database/smartassist.db # Auto-created on first run
└── documentation/
```

## Tech Stack
Python 3.10+ · Flask · SQLite · Werkzeug · Chart.js · Vanilla JS

## Notes for Submission
- Replace the secret key in `app.py` before deploying.
- Change the default admin password after first login.

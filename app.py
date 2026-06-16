"""SmartAssist AI - Customer Service Chatbot (Flask)
Run: pip install -r requirements.txt && python app.py
Login: admin / admin123
"""
import os, sqlite3, json, datetime, re
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.security import generate_password_hash, check_password_hash
from chatbot_model import get_bot_reply
from sentiment_model import analyze_sentiment
from intent_classifier import classify_intent

APP_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(APP_DIR, "database", "smartassist.db")

app = Flask(__name__)
app.secret_key = "smartassist-secret-key-change-me"

# ---------- DB ----------
def db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = db(); c = conn.cursor()
    c.executescript("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS chats(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        message TEXT NOT NULL,
        reply TEXT NOT NULL,
        intent TEXT,
        sentiment TEXT,
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS faqs(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question TEXT NOT NULL,
        answer TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS tickets(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        subject TEXT NOT NULL,
        description TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'open',
        created_at TEXT NOT NULL
    );
    """)
    # Seed admin
    c.execute("SELECT id FROM users WHERE username='admin'")
    if not c.fetchone():
        c.execute("INSERT INTO users(username,password_hash,created_at) VALUES(?,?,?)",
                  ("admin", generate_password_hash("admin123"), datetime.datetime.utcnow().isoformat()))
    # Seed FAQs
    c.execute("SELECT COUNT(*) FROM faqs")
    if c.fetchone()[0] == 0:
        seeds = [
            ("How do I reset my password?", "Go to Settings > Security > Reset Password and follow the email link."),
            ("How can I track my order?", "Open the Orders page and click 'Track' next to your order."),
            ("What is your refund policy?", "We offer full refunds within 30 days of purchase."),
            ("How do I contact human support?", "Create a ticket from the Tickets page and an agent will respond within 24 hours."),
            ("What are your business hours?", "Our support team is available 24/7 via chat."),
        ]
        c.executemany("INSERT INTO faqs(question,answer) VALUES(?,?)", seeds)
    conn.commit(); conn.close()

# ---------- Auth ----------
def login_required(f):
    from functools import wraps
    @wraps(f)
    def wrap(*a, **kw):
        if "user_id" not in session:
            return redirect(url_for("login"))
        return f(*a, **kw)
    return wrap

@app.route("/")
def landing():
    return render_template("landing.html")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        u = request.form.get("username","").strip()
        p = request.form.get("password","")
        conn = db()
        row = conn.execute("SELECT * FROM users WHERE username=?", (u,)).fetchone()
        conn.close()
        if row and check_password_hash(row["password_hash"], p):
            session["user_id"] = row["id"]; session["username"] = row["username"]
            return redirect(url_for("dashboard"))
        flash("Invalid username or password", "error")
    return render_template("login.html")
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        if not username:
            flash("Username is required", "error")
            return redirect(url_for("register"))

        if not password:
            flash("Password is required", "error")
            return redirect(url_for("register"))

        if password != confirm_password:
            flash("Passwords do not match", "error")
            return redirect(url_for("register"))

        conn = db()

        existing_user = conn.execute(
            "SELECT * FROM users WHERE username=?",
            (username,)
        ).fetchone()

        if existing_user:
            conn.close()
            flash("Username already exists", "error")
            return redirect(url_for("register"))

        conn.execute(
            "INSERT INTO users(username, password_hash, created_at) VALUES (?, ?, ?)",
            (
                username,
                generate_password_hash(password),
                datetime.datetime.utcnow().isoformat()
            )
        )

        conn.commit()
        conn.close()

        flash("Account created successfully. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ---------- Pages ----------
@app.route("/dashboard")
@login_required
def dashboard():
    conn = db()
    total_chats = conn.execute("SELECT COUNT(*) FROM chats").fetchone()[0]
    open_tickets = conn.execute("SELECT COUNT(*) FROM tickets WHERE status='open'").fetchone()[0]
    faq_count = conn.execute("SELECT COUNT(*) FROM faqs").fetchone()[0]
    recent = conn.execute("SELECT * FROM chats ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()
    return render_template("dashboard.html",
        total_chats=total_chats, open_tickets=open_tickets,
        faq_count=faq_count, recent=recent)

@app.route("/chatbot")
@login_required
def chatbot():
    return render_template("chatbot.html")

@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data = request.get_json(force=True)
    msg = (data.get("message") or "").strip()
    if not msg:
        return jsonify({"error":"empty"}), 400
    intent = classify_intent(msg)
    sentiment = analyze_sentiment(msg)
    reply = get_bot_reply(msg, intent, db)
    conn = db()
    conn.execute("INSERT INTO chats(user_id,message,reply,intent,sentiment,created_at) VALUES(?,?,?,?,?,?)",
                 (session["user_id"], msg, reply, intent, sentiment, datetime.datetime.utcnow().isoformat()))
    conn.commit(); conn.close()
    return jsonify({"reply": reply, "intent": intent, "sentiment": sentiment})

@app.route("/analytics")
@login_required
def analytics():
    conn = db()
    rows = conn.execute("SELECT intent, COUNT(*) c FROM chats GROUP BY intent").fetchall()
    sentiments = conn.execute("SELECT sentiment, COUNT(*) c FROM chats GROUP BY sentiment").fetchall()
    by_day = conn.execute("SELECT substr(created_at,1,10) d, COUNT(*) c FROM chats GROUP BY d ORDER BY d DESC LIMIT 14").fetchall()
    conn.close()
    return render_template("analytics.html",
        intents=[dict(r) for r in rows],
        sentiments=[dict(r) for r in sentiments],
        by_day=list(reversed([dict(r) for r in by_day])))

@app.route("/faq", methods=["GET","POST"])
@login_required
def faq():
    conn = db()
    if request.method == "POST":
        q = request.form.get("question","").strip()
        a = request.form.get("answer","").strip()
        if q and a:
            conn.execute("INSERT INTO faqs(question,answer) VALUES(?,?)", (q,a))
            conn.commit()
        return redirect(url_for("faq"))
    items = conn.execute("SELECT * FROM faqs ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("faq.html", items=items)

@app.route("/faq/delete/<int:fid>")
@login_required
def faq_delete(fid):
    conn = db(); conn.execute("DELETE FROM faqs WHERE id=?", (fid,)); conn.commit(); conn.close()
    return redirect(url_for("faq"))

@app.route("/tickets", methods=["GET","POST"])
@login_required
def tickets():
    conn = db()
    if request.method == "POST":
        s = request.form.get("subject","").strip()
        d = request.form.get("description","").strip()
        if s and d:
            conn.execute("INSERT INTO tickets(user_id,subject,description,created_at) VALUES(?,?,?,?)",
                         (session["user_id"], s, d, datetime.datetime.utcnow().isoformat()))
            conn.commit()
        return redirect(url_for("tickets"))
    items = conn.execute("SELECT * FROM tickets ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("tickets.html", items=items)

@app.route("/tickets/close/<int:tid>")
@login_required
def ticket_close(tid):
    conn = db(); conn.execute("UPDATE tickets SET status='closed' WHERE id=?", (tid,)); conn.commit(); conn.close()
    return redirect(url_for("tickets"))

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)

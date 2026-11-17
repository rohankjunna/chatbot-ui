

import os, re
import pandas as pd
import joblib, json, sqlite3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime
from nltk.stem import WordNetLemmatizer
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from openai import OpenAI

# ─────────────────────────
# APP
# ─────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────
# TEXT CLEANING + SYNONYMS
# ─────────────────────────
lemmatizer = WordNetLemmatizer()

SYNONYMS = {
    "fees": ["price", "cost", "charge"],
    "demo": ["trial", "sample"],
    "subject": ["course", "topic"],
    "tutor": ["teacher", "faculty"]
}

def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)
    words = []
    for w in text.split():
        w = lemmatizer.lemmatize(w)
        for key, vals in SYNONYMS.items():
            if w in vals:
                w = key
        words.append(w)
    return " ".join(words)

# ─────────────────────────
# LOAD MODELS
# ─────────────────────────
try:
    ml_model = joblib.load("model.pkl")
except:
    ml_model = None

try:
    with open("responses.json", encoding="utf-8") as f:
        responses = json.load(f)
except:
    responses = {}

try:
    df = pd.read_csv("dataset.csv", on_bad_lines="skip")
    df["pattern"] = df["pattern"].astype(str).str.lower().str.strip()
    df["response"] = df["response"].astype(str).str.strip()
    embed_model = SentenceTransformer("all-MiniLM-L6-v2")
    patterns = df["pattern"].tolist()
    pattern_embeddings = embed_model.encode(patterns)
except:
    df = None

# ─────────────────────────
# GROK CLIENT
# ─────────────────────────
client = OpenAI(
    api_key=os.getenv("GROK_API_KEY"),
    base_url="https://api.x.ai/v1"
)

# ─────────────────────────
# MEMORY
# ─────────────────────────
sessions = {}

# ─────────────────────────
# MODELS
# ─────────────────────────
class ChatRequest(BaseModel):
    user_id: str
    message: str

# ─────────────────────────
# DB
# ─────────────────────────
def get_db():
    conn = sqlite3.connect("chatbot.db")
    conn.row_factory = sqlite3.Row
    return conn

def save_message(user_id, role, message):
    conn = sqlite3.connect("chatbot.db")
    conn.execute(
        "INSERT INTO chat_logs (user_id, role, message, timestamp) VALUES (?, ?, ?, ?)",
        (user_id, role, message, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

# ─────────────────────────
# FAQ
# ─────────────────────────
FAQ_RESPONSES = {
    "fees": "💰 Fees start from ₹2000/month.",
    "demo": "🎓 We provide demo classes.",
    "subjects": "📚 Maths, Science, English available.",
    "tutor": "👨‍🏫 Verified tutors available.",
    "online": "💻 Online classes available.",
    "home": "🏠 Home tuition available."
}

# ─────────────────────────
# CHAT
# ─────────────────────────
@app.post("/chat")
def chat(req: ChatRequest):
    user_id = req.user_id
    msg = clean_text(req.message)

    save_message(user_id, "user", msg)

    if not msg:
        return {"reply": "Please type something 😊"}

    if user_id not in sessions:
        sessions[user_id] = {"step": "greeting"}

    session = sessions[user_id]

    # GREETING
    if msg in ["hi", "hello", "hey", "start"]:
        sessions[user_id] = {"step": "greeting"}
        return {"reply": "Hi 👋 Ask about fees, demo or type 'book'."}

    # CLASS DETECTION
    if  "class  " in msg  or "class " in msg:
        return {"reply": "📚 Yes! We provide tutors for Class "}

    # BOOKING FLOW
    if msg in ["book", "register", "find tutor"] or session["step"] != "greeting":

        if session["step"] == "greeting":
            session["step"] = "ask_name"
            return {"reply": "What is your name?"}

        elif session["step"] == "ask_name":
            session["name"] = msg
            session["step"] = "ask_class"
            return {"reply": "Which class?"}

        elif session["step"] == "ask_class":
            session["class"] = msg
            session["step"] = "ask_subject"
            return {"reply": "Which subject?"}

        elif session["step"] == "ask_subject":
            session["subject"] = msg
            session["step"] = "ask_mode"
            return {"reply": "Home or Online?"}

        elif session["step"] == "ask_mode":
            session["mode"] = msg
            session["step"] = "ask_city"
            return {"reply": "📍 Which city are you in?"}

        elif session["step"] == "ask_city":
            session["city"] = msg
            session["step"] = "ask_contact"
            return {"reply": "📞 Your contact number?"}

        elif session["step"] == "ask_contact":
            # Normalize number
            contact = req.message.strip().replace(" ", "").replace("+", "")
            if contact.isdigit() and len(contact) == 10:
                contact = "91" + contact

            session["contact"] = contact

            conn = get_db()
            conn.execute(
                "INSERT INTO leads (name, class, subject, location, mode, contact) VALUES (?, ?, ?, ?, ?, ?)",
                (
                    session.get("name", "NA"),
                    session.get("class", "NA"),
                    session.get("subject", "NA"),
                    session.get("city", "NA"),
                    session.get("mode", "NA"),
                    contact
                )
            )
            conn.commit()
            conn.close()

            sessions[user_id] = {"step": "greeting"}
            return {"reply": f"✅ Done! We will call you on {contact} shortly 😊"}

    # FAQ
    for key in FAQ_RESPONSES:
        if key in msg:
            return {"reply": FAQ_RESPONSES[key]}

    # DB FAQ
    conn = get_db()
    rows = conn.execute("SELECT answer, keywords FROM faqs").fetchall()
    conn.close()

    for r in rows:
        if r["keywords"] and any(k in msg for k in r["keywords"].split(",")):
            return {"reply": r["answer"]}

    # CSV AI
    if df is not None:
        emb = embed_model.encode([msg])
        sim = cosine_similarity(emb, pattern_embeddings)[0]
        idx = sim.argmax()
        if sim[idx] > 0.5:
            return {"reply": df.iloc[idx]["response"]}

    # ML MODEL
    if ml_model:
        intent = ml_model.predict([msg])[0]
        conf = ml_model.predict_proba([msg]).max()
        print("Intent:", intent, "Confidence:", conf)
        if conf > 0.4:
            return {"reply": responses.get(intent, "I didn't understand")}

    # GROK FALLBACK
    try:
        res = client.chat.completions.create(
            model="grok-beta",
            messages=[
                {"role": "system", "content": "You are a helpful tutor assistant."},
                {"role": "user", "content": msg}
            ]
        )
        return {"reply": res.choices[0].message.content}
    except Exception as e:
        print("Grok error:", e)
        return {"reply": "🤔 Try asking about fees, demo or type 'book'."}

# ─────────────────────────
# ROUTES
# ─────────────────────────
@app.get("/")
def home():
    return {"message": "Backend running 🚀"}

@app.get("/leads")
def get_leads():
    conn = get_db()
    data = conn.execute("SELECT * FROM leads").fetchall()
    conn.close()
    return [dict(row) for row in data]

@app.get("/export")
def export_leads():
    conn = get_db()
    data = conn.execute("SELECT * FROM leads").fetchall()
    conn.close()

    df_export = pd.DataFrame([dict(row) for row in data])
    filepath = "/tmp/leads_export.xlsx"
    df_export.to_excel(filepath, index=False)

    return FileResponse(
        path=filepath,
        filename="leads.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
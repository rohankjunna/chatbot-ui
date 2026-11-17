import json, nltk, joblib, pandas as pd, re
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score

nltk.download('wordnet')
lemmatizer = WordNetLemmatizer()

# 🔥 SYNONYMS (BOOST ACCURACY)
SYNONYMS = {
    "fees": ["price", "cost", "charge"],
    "demo": ["trial", "sample"],
    "subject": ["course", "topic"],
    "tutor": ["teacher", "faculty"]
}

# 🔥 CLEAN FUNCTION
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

# ── Load CSV ──────────────────────────
df = pd.read_csv("dataset.csv", on_bad_lines="skip")

df["intent"]   = df["intent"].astype(str).str.strip()
df["pattern"]  = df["pattern"].astype(str).str.strip()
df["response"] = df["response"].astype(str).str.strip()

df = df[df["pattern"].str.len() > 1]
df = df[df["intent"].str.len() > 1]

print(f"Loaded {len(df)} rows")

# ── Prepare Data ──────────────────────
X = df["pattern"].apply(clean_text)
y = df["intent"]

# 🔥 TRAIN / TEST SPLIT
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# ── MODEL ─────────────────────────────
model = Pipeline([
    ("tfidf", TfidfVectorizer(
        ngram_range=(1, 3),
        max_features=5000
    )),
    ("clf", LogisticRegression(max_iter=2000))
])

# ── TRAIN ─────────────────────────────
model.fit(X_train, y_train)

# ── EVALUATE 🔥
y_pred = model.predict(X_test)
acc = accuracy_score(y_test, y_pred)

print(f"\n🔥 Accuracy: {acc * 100:.2f}%")

# ── SAVE ─────────────────────────────
joblib.dump(model, "model.pkl")

responses = dict(zip(df["intent"], df["response"]))

with open("responses.json", "w", encoding="utf-8") as f:
    json.dump(responses, f, ensure_ascii=False, indent=2)

print("✅ Model saved!")
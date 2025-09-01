# nlu.py
# Simple NLU using TF-IDF + LinearSVC. Trains from dataset.csv and saves model and vectorizer.
from __future__ import annotations

import os, re, joblib, pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

MODELS_DIR = os.path.join(os.path.dirname(__file__), "models")
MODEL_PATH = os.path.join(MODELS_DIR, "intent_model.joblib")

def ensure_model(data_path: str) -> Pipeline:
    """Train the intent classifier if missing. Returns a scikit-learn Pipeline."""
    os.makedirs(MODELS_DIR, exist_ok=True)
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)

    df = pd.read_csv(data_path)
    df["text"] = df["text"].astype(str).str.lower()
    clf = Pipeline([
        ("tfidf", TfidfVectorizer(ngram_range=(1,2), min_df=1)),
        ("svm", LinearSVC())
    ])
    clf.fit(df["text"], df["intent"])
    joblib.dump(clf, MODEL_PATH)
    return clf

_model: Pipeline | None = None

def load_or_train(dataset_csv: str) -> Pipeline:
    global _model
    if _model is None:
        _model = ensure_model(dataset_csv)
    return _model

def get_intent(utterance: str, dataset_csv: str) -> str:
    """Return predicted intent label for utterance."""
    model = load_or_train(dataset_csv)
    try:
        return model.predict([utterance.lower()])[0]
    except Exception:
        return "help"

# -------- Entity Extraction (regex) --------
AMOUNT_RE = re.compile(r'(?i)(?:rs\.?|inr|₹)?\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]{1,2})?|[0-9]+)')
NAME_RE = re.compile(r'(?i)(?:to|for|send to|transfer to)\s+([a-zA-Z][a-zA-Z ]{1,30})')

def parse_amount(text: str) -> float | None:
    m = AMOUNT_RE.search(text.replace(",", ""))
    if not m:
        # try words like 'two thousand'
        words = {
            "one":1,"two":2,"three":3,"four":4,"five":5,"six":6,"seven":7,"eight":8,"nine":9,"ten":10,
            "eleven":11,"twelve":12,"thirteen":13,"fourteen":14,"fifteen":15,"sixteen":16,"seventeen":17,"eighteen":18,"nineteen":19,
            "twenty":20,"thirty":30,"forty":40,"fifty":50,"sixty":60,"seventy":70,"eighty":80,"ninety":90,
            "hundred":100,"thousand":1000
        }
        tokens = text.lower().split()
        total = 0; cur = 0; found = False
        for tok in tokens:
            if tok in words:
                found = True
                val = words[tok]
                if val in (100,1000):
                    cur = max(1, cur) * val
                    total += cur; cur = 0
                else:
                    cur += val
        if found:
            return float(total + cur)
        return None
    try:
        return float(m.group(1))
    except Exception:
        return None

def parse_name(text: str) -> str | None:
    m = NAME_RE.search(text)
    if m:
        return m.group(1).strip().title()
    # fallback: after 'to ' take next token
    low = text.lower()
    if " to " in low:
        after = low.split(" to ",1)[1].split()
        if after:
            return after[0].title()
    return None

# backend/app_flask.py
from flask import Flask, request, jsonify
from flask_cors import CORS
import joblib
import math

app = Flask(__name__)
CORS(app)

# load model + vectorizer (make sure these files exist in backend/)
print("Loading model & vectorizer...")
model = joblib.load("model.pkl")         # RandomForest
vectorizer = joblib.load("vectorizer.pkl")  # TfidfVectorizer
print("Loaded model and vectorizer.")

def explain_from_url(url):
    reasons = []
    u = url.lower()
    if "@" in u:
        reasons.append("Contains '@' symbol")
    if any(token in u for token in ["login","secure","verify","account","update","signin","pay","bank"]):
        reasons.append("Contains suspicious token (login/secure/verify/etc)")
    if len(u) > 75:
        reasons.append("Long URL (>75 chars)")
    if any(ch in u for ch in ['%','\\','{','}','<','>']):
        reasons.append("Contains special/encoded chars")
    if not reasons:
        reasons = ["No obvious heuristics matched"]
    return reasons

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.get_json() or {}
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "Missing url"}), 400

    # vectorize URL text the same way as in training
    try:
        X = vectorizer.transform([url])
        prob = float(model.predict_proba(X)[0][1])
    except Exception as e:
        return jsonify({"error": "Model error", "detail": str(e)}), 500

    score = int(round(prob * 100))
    if score >= 60:
        label = "MALICIOUS"
    elif score >= 35:
        label = "SUSPICIOUS"
    else:
        label = "SAFE"

    reasons = explain_from_url(url)

    return jsonify({
        "url": url,
        "label": label,
        "score": score,
        "reasons": reasons
    })

if __name__ == "__main__":
    # default Flask port 5000; you may run behind different host/port
    app.run(host="0.0.0.0", port=5000, debug=True)

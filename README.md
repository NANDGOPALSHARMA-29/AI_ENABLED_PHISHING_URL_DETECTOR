# PhishDetector

End-to-end phishing URL detection project with:
- A Flask ML API for classifying URLs.
- A static web UI for quick checks.
- A Chrome extension that classifies the active tab.
- Data prep + training scripts for model updates.

## Live Demo
```
https://aiphishdetector.netlify.app/
```

## What’s Inside
- `backend/` Flask API, model training, and saved model artifacts.
- `frontend/` Static single-page UI that calls the API.
- `phish-checker-extension/` Chrome extension (MV3) that scores the current tab URL.
- `data/` Data conversion and training helper scripts + datasets.

## How It Works
- Training (`backend/train_real.py`) builds a TF‑IDF + RandomForest model from URL text.
- The Flask API (`backend/app_flask.py`) loads `model.pkl` and `vectorizer.pkl` to score URLs.
- The UI and extension send a URL to the API and display the label, score, and reasons.

## API
`POST /analyze`
```json
{ "url": "https://example.com/login" }
```
Response (example):
```json
{
  "url": "...",
  "label": "SAFE | SUSPICIOUS | MALICIOUS",
  "score": 0-100,
  "reasons": ["..."]
}
```

## Quick Start (Backend)
1. Create and activate a virtual environment (recommended).
2. Install dependencies:
   - `pip install -r backend/requirements.txt`
3. Run the API:
   - `python backend/app_flask.py`
4. Test:
   - `POST http://127.0.0.1:5000/analyze`

## Train / Refresh the Model
There are two training flows:
- **Synthetic data**: `backend/train.py` (generates fake URLs).
- **Real data**: `backend/train_real.py` (uses `data/openphish_norm.csv` and `data/benign_norm.csv`).

Typical real-data flow:
1. Put raw files in `data/`:
   - `openphish_raw.txt`
   - `benign_raw.csv` (must include a `domain` column)
2. Run the conversion helper:
   - `powershell -File data/prepare_and_train.ps1`
   - Add `-RunTraining` to auto-train after conversion.
3. Training outputs:
   - `backend/model.pkl`
   - `backend/vectorizer.pkl`

## Frontend
`frontend/index.html` is a static page that calls a backend URL configured in the script.
By default it points to a hosted API (`onrender.com`). Update the fetch URL if you want to use your local API.

## Chrome Extension (PhishGuard)
1. Open Chrome → `chrome://extensions`
2. Enable **Developer mode**
3. Click **Load unpacked** and select `phish-checker-extension/`
4. Update the backend URL in:
   - `phish-checker-extension/background.js`

## Project Structure
- `backend/app_flask.py` — Flask API (`/analyze`)
- `backend/train_real.py` — TF‑IDF + RandomForest training
- `backend/model.pkl` / `backend/vectorizer.pkl` — saved model artifacts
- `frontend/index.html` — static UI
- `phish-checker-extension/` — Chrome extension code
- `data/prepare_and_train.ps1` — data conversion + optional training

## Notes / Gotchas
- The extension currently posts to `http://127.0.0.1:5000/classify` by default, but the API route is `/analyze`.
  Update the extension or add a `/classify` route if needed.
- `backend/venv/` is checked in; you can ignore it and create your own environment.

# 🛡️ ScamShield AI

**Fake Job & Internship Scam Detection System** · Detect. Explain. Report. Protect, before you pay.

ScamShield AI is a web application that helps students check job and internship offers for common scam patterns, and helps recruiters check resumes for inconsistencies. It uses rule-based risk analysis (including Tamil/Tanglish phrases) and explains every result.

## 📌 Problem Statement

Many students receive fake job offers that ask for a registration fee, collect Aadhaar, PAN and bank details, or arrive as WhatsApp/Telegram chats that are hard to verify. Recruiters also receive fake or inflated resumes. Most victims realise only after money is lost.

ScamShield AI gives an accessible first check, clear reasons, and a ready complaint draft.

## 🚀 Features

| Feature | Description |
|---|---|
| 🔍 Student Mode | Paste a job message and get a Low / Uncertain / High risk level with a 0-100 score |
| 🧠 Explainable Results | Risky words are highlighted and each matched red flag is listed |
| 🏷️ Scam Type | Registration fee scam, document harvesting or fake chat recruitment |
| 🗣️ Tamil & Tanglish Rules | Detects phrases like "fees kattunga", "panam anuppunga", "udane join" |
| 📝 Complaint Draft | Pre-filled draft for cybercrime.gov.in with the 1930 helpline |
| 💬 Safe Reply Helper | Questions to ask a recruiter before replying |
| 👔 Recruiter Mode | Resume checks: overlapping timelines, future dates, inflated experience, copied lines, keyword stuffing |
| 📈 Live Dashboard | Scans, risk levels, top red-flag words and a live feed, refreshed every 3 seconds |
| 🎮 Scam or Real? | 6-question awareness game with explanations |

## 🏗️ System Architecture

```
Browser (HTML / CSS / JS)        Streamlit UI (streamlit_app.py)
            ↓                                  ↓
        Flask routes (app.py)  ←── shared logic ──→
            ↓
 Rule Engine: scan_offer() · check_resume()
            ↓
 In-memory stats (dashboard)
```

## 📁 Project Structure

```
ScamShield_AI_Website/
├── app.py               # Flask app, rule engine, resume checker, game data, stats API
├── streamlit_app.py     # Streamlit version (reuses logic from app.py)
├── templates/           # base, index, recruiter, dashboard, game, about (Jinja2)
├── static/style.css     # Dark theme styles
├── requirements.txt
├── Procfile · runtime.txt
└── README.md
```

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Frontend | HTML5, CSS3, JavaScript |
| Backend | Python 3.11, Flask |
| Alternate UI | Streamlit |
| Detection | Keyword / rule engine |
| Hosting | Streamlit Community Cloud or Render |

## 🔌 Routes

| Method | Endpoint | Description |
|---|---|---|
| GET, POST | `/` | Student Mode scanner |
| GET, POST | `/recruiter` | Resume verification |
| GET | `/dashboard` | Live dashboard page |
| GET | `/api/stats` | Live stats as JSON |
| GET | `/game` | Scam or Real? game |
| GET | `/about` | About page |

## 🧪 How Detection Works

1. The message is lowercased and checked against a list of red-flag phrases.
2. Score = 18 points per matched flag, capped at 95.
3. Score 54 or more is **High**, 18 to 53 is **Uncertain**, below 18 is **Low**.
4. Matched phrases are highlighted and mapped to a scam type.

This is a rule-based demo. It is **not** a trained machine-learning model.

## ▶️ Getting Started

```bash
pip install -r requirements.txt
python app.py                      # Flask version → http://127.0.0.1:5000
streamlit run streamlit_app.py     # Streamlit version
```

Windows PowerShell: if `activate` is blocked, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.

## ☁️ Deployment

- **Streamlit Community Cloud:** push to a public GitHub repo, create an app on share.streamlit.io, set main file to `streamlit_app.py`.
- **Render:** create a Web Service from the repo; the included `Procfile` is used.

## ⚠️ Current Limitations

- No trained ML model (TF-IDF + Logistic Regression is planned)
- No screenshot / PDF OCR
- Dashboard data is in memory and resets on restart (starts with demo baseline numbers)
- Resume checks work on pasted text only; hidden-text detection is not included

## 📌 Future Work

- 🤖 TF-IDF + Logistic Regression model with SHAP/LIME explanations
- 📷 OCR for WhatsApp/Telegram screenshots and PDF offer letters
- 🏢 Company reviews and domain-age checks
- 🗄️ Database for permanent scan history and reports
- 🔐 User login and an admin dashboard

## 👥 Team

Sivadharshini S · Sruthiks G · Subiksha D · Yogalakshme M

## ⚠️ Disclaimer

ScamShield AI provides risk analysis based on simple rules and known scam patterns. It does not guarantee accuracy, and a low score never proves an offer is genuine. Report fraud at https://cybercrime.gov.in or call 1930.

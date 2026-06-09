# ATS Resume Scanner

A modern full-stack web app that analyzes your resume against a job description using Google's Gemini AI. Get an ATS compatibility score, missing skills, missing keywords, and actionable improvement suggestions.

![Stack](https://img.shields.io/badge/React-18-61DAFB?style=flat-square)
![Stack](https://img.shields.io/badge/Tailwind-3-38B2AC?style=flat-square)
![Stack](https://img.shields.io/badge/Flask-3-000000?style=flat-square)
![Stack](https://img.shields.io/badge/Gemini-AI-8B5CF6?style=flat-square)

## Features

- **PDF resume upload** — drag & drop or file picker
- **Job description input** — paste the full posting
- **AI analysis** — powered by Google Gemini
- **Dashboard results**:
  - ATS score (0–100) with visual ring
  - Missing skills
  - Missing keywords
  - Resume improvement suggestions

## Project Structure

```
ats-resume-scanner/
├── backend/
│   ├── app.py                    # Flask API entry point
│   ├── requirements.txt
│   ├── .env.example
│   └── services/
│       ├── pdf_extractor.py      # pdfplumber text extraction
│       └── gemini_analyzer.py    # Gemini API integration
├── frontend/
│   ├── src/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   └── components/
│   │       ├── Header.jsx
│   │       ├── UploadSection.jsx
│   │       ├── JobDescription.jsx
│   │       ├── LoadingSpinner.jsx
│   │       └── ResultsDashboard.jsx
│   ├── package.json
│   └── vite.config.js            # Proxies /api → Flask
└── README.md
```

## Prerequisites

- **Python 3.10+**
- **Node.js 18+**
- **Gemini API key** — get one free at [Google AI Studio](https://aistudio.google.com/apikey)

## Setup

### 1. Backend (Flask)

```bash
cd ats-resume-scanner/backend

# Create and activate virtual environment
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env        # Windows
# cp .env.example .env        # macOS / Linux

# Edit .env and set your Gemini API key:
# GEMINI_API_KEY=your_actual_key_here

# Start the API server
python app.py
```

The API runs at **http://localhost:5000**.

Health check: `GET http://localhost:5000/api/health`

### 2. Frontend (React + Vite)

Open a **new terminal**:

```bash
cd ats-resume-scanner/frontend

npm install
npm run dev
```

The app runs at **http://localhost:5173**. Vite proxies `/api` requests to Flask automatically.

### 3. Use the App

1. Open http://localhost:5173 in your browser
2. Upload a PDF resume
3. Paste the job description
4. Click **Analyze Resume**
5. Review your ATS score and recommendations

## API Reference

### `POST /api/analyze`

**Content-Type:** `multipart/form-data`

| Field             | Type | Required | Description        |
|-------------------|------|----------|--------------------|
| `resume`          | file | Yes      | PDF resume file    |
| `job_description` | text | Yes      | Job posting text   |

**Success response (200):**

```json
{
  "ats_score": 72,
  "missing_skills": ["Kubernetes", "CI/CD"],
  "missing_keywords": ["agile methodology", "cross-functional"],
  "suggestions": ["Add a Skills section with cloud technologies", "..."]
}
```

**Error response (4xx/5xx):**

```json
{
  "error": "Error message here"
}
```

## Configuration

| Variable         | Default | Description                    |
|------------------|---------|--------------------------------|
| `GEMINI_API_KEY` | —       | Required. Google Gemini API key |
| `FLASK_PORT`     | `5000`  | Flask server port              |

To use a different Gemini model, edit `backend/services/gemini_analyzer.py` and change the model name (e.g. `gemini-2.0-flash`, `gemini-1.5-pro`).

For production frontend builds pointing at a remote API:

```bash
# frontend/.env.production
VITE_API_URL=https://your-api.example.com
```

## Production Build

```bash
# Frontend
cd frontend
npm run build
# Output in frontend/dist/

# Backend — use a production WSGI server
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `GEMINI_API_KEY is not set` | Create `backend/.env` from `.env.example` and add your key |
| Empty PDF text | PDF may be image-only; use a text-based or OCR'd resume |
| CORS errors | Ensure Flask is running on port 5000; Vite proxy handles dev CORS |
| `ModuleNotFoundError` | Activate the Python venv before running `python app.py` |
| pip fails building `cffi` on Windows | Install [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/), then retry `pip install` |

## License

MIT

# AI Recruiter Mock Interview 🎙️

A production-grade AI-powered mock interview practice platform powered by **Google Gemini 3.6** and featuring **Alex Rivera**, a Senior Technical Recruiter and Principal Bar Raiser persona.

---

## ✨ Features

- **Google Gemini Deep Reasoning Engine**:
  - Powered by `gemini-3.6-flash` using the official `google-genai` SDK.
  - Tailors screening questions to the candidate's uploaded resume or LinkedIn profile.
  - Generates deep, multi-dimensional Bar Raiser evaluation reports with Plotly Competency Radar charts.
- **Three-Tier Resilient Voice Engine**:
  - **Tier 1 (Gemini Native TTS)**: Authenticated speech synthesis (`gemini-2.5-flash-preview-tts`) with voice `Charon`.
  - **Tier 2 (Google TTS - gTTS)**: Free backup text-to-speech.
  - **Tier 3 (Browser SpeechSynthesis)**: Client-side voice synthesis guaranteeing the avatar always speaks.
- **Simli Real-Time Avatar Integration**:
  - WebRTC-based live talking avatar stream with synchronized speech lip-syncing.
- **Comprehensive Candidate Scorecard**:
  - 0–100 Overall Fit Score & Hiring Recommendation badge.
  - Interactive Plotly Competency Radar Chart across 5 core dimensions.
  - Question-by-question breakdown comparing candidate transcripts with gold-standard STAR benchmark answers.
  - Downloadable Markdown evaluation report.

---

## 🚀 Quickstart Guide

### 1. Setup & Install Dependencies
```bash
python -m venv venv
# Windows:
.\venv\Scripts\Activate.ps1
# macOS / Linux:
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Local Secrets
Create a `.streamlit/secrets.toml` file (this file is excluded by `.gitignore`):
```toml
GEMINI_API_KEY = "your-gemini-api-key"
SIMLI_API_KEY = "your-simli-api-key"
SIMLI_FACE_ID = "5514e24d-6086-46a3-ace4-6a7264e5cb7c"
```

### 3. Launch the Application
```bash
streamlit run app.py
```

---

## ☁️ Deploy to Render

1. **Build Command**:
   ```bash
   pip install -r requirements.txt
   ```
2. **Start Command**:
   ```bash
   streamlit run app.py --server.port $PORT --server.address 0.0.0.0 --server.headless true
   ```
3. **Environment Variables**:
   Add `GEMINI_API_KEY`, `SIMLI_API_KEY`, and `SIMLI_FACE_ID` under your Render Web Service Environment settings.

# AI Recruiter Mock Interview 🎙️

A production-grade AI-powered mock interview practice platform powered by **Google Gemini 3.6** and featuring **Alex Rivera**, a Senior Technical Recruiter and Principal Bar Raiser persona.

---

## ✨ Features

- **Google Gemini Deep Reasoning Engine**:
  - Powered by `gemini-3.6-flash` / `gemini-2.5-pro` using the official `google-genai` SDK.
  - Generates deep, scenario-grounded technical & behavioral questions tailored to target job role, experience level, and candidate resume.
  - Produces multi-dimensional, deep analytical evaluations strictly grounded in candidate transcripts with zero canned presets.
- **Multimodal Voice & Audio Intelligence**:
  - Live microphone recording with Gemini multimodal audio transcription (`audio/wav`).
  - gTTS audio playback integrated via base64 `<audio autoplay>` for zero-friction listening.
- **Simli Real-Time Avatar Integration**:
  - WebRTC-based live talking avatar stream with sub-300ms speech-to-video lip-syncing.
- **Dynamic State Machine**:
  - `Setup` ➡️ `Live Interview (3-5 Questions)` ➡️ `Deep Scorecard & Radar Chart`.
- **Strict Input Validation**:
  - Real-time word counter enforcing a minimum of 5 words before allowing answer submission.
- **Comprehensive Scorecard**:
  - Overall Score (0-100) & Hiring Recommendation badge.
  - Interactive Plotly Competency Radar Chart across 5 core dimensions.
  - Detailed Question-by-Question Deep Dive with strengths, omissions, and gold-standard model STAR answers.
  - Downloadable Markdown evaluation report (`.md`).

---

## 🚀 Quickstart Guide

### 1. Activate the Virtual Environment

**Windows PowerShell:**
```powershell
.\venv\Scripts\Activate.ps1
```

**macOS / Linux:**
```bash
source venv/bin/activate
```

### 2. Launch the Application
```bash
streamlit run app.py
```

---

## 🔑 Secrets Configuration

Configure your keys in [`.streamlit/secrets.toml`](file:///.streamlit/secrets.toml):


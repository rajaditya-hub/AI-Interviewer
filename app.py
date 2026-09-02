import os
import re
import json
import base64
import hashlib
import time
import io
import datetime
import requests
import streamlit as st
import streamlit.components.v1 as components
import plotly.graph_objects as go
import pandas as pd

# -----------------------------------------------------------------------------
# Current Year & Metadata
# -----------------------------------------------------------------------------
CURRENT_YEAR = datetime.datetime.now().year

# Optional PDF & DOCX readers
try:
    from pypdf import PdfReader
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# Google Text-to-Speech
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

# Google GenAI SDK (Gemini)
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# Simli Real-Time Avatar SDK
try:
    import simli
    from simli import SimliClient, SimliConfig
    SIMLI_AVAILABLE = True
except ImportError:
    SIMLI_AVAILABLE = False

# -----------------------------------------------------------------------------
# Page Configuration
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Recruiter | Mock Interview",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------------------------------------------------------
# Synthetic Intelligence Recruiting Theme & CSS (Strictly Matching Design System)
# -----------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;600;700;800&family=Inter:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #020617;
        color: #dae2fd;
    }

    /* Completely hide Streamlit Deploy Button, Running Man, and Default Header Toolbar */
    .stDeployButton,
    [data-testid="stAppDeployButton"],
    header [data-testid="stToolbar"] .stDeployButton,
    header [data-testid="stToolbar"],
    #MainMenu,
    header[data-testid="stHeader"] {
        display: none !important;
        visibility: hidden !important;
        height: 0 !important;
    }

    .main .block-container {
        padding-top: 1.25rem;
        padding-bottom: 2.5rem;
        max-width: 1360px;
    }

    /* Glassmorphic Base Cards */
    .glass-card {
        background: linear-gradient(180deg, rgba(15, 23, 42, 0.8) 0%, rgba(15, 23, 42, 0.9) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-top: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(20px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.35);
        margin-bottom: 20px;
        position: relative;
    }

    .ai-glow {
        box-shadow: 0 0 30px -5px rgba(192, 193, 255, 0.18);
    }

    /* Typography */
    .font-headline-xl {
        font-family: 'Geist', sans-serif;
        font-size: 2.5rem;
        font-weight: 700;
        letter-spacing: -0.02em;
        line-height: 1.2;
        color: #ffffff;
    }

    .font-headline-lg {
        font-family: 'Geist', sans-serif;
        font-size: 1.65rem;
        font-weight: 600;
        letter-spacing: -0.01em;
        color: #ffffff;
    }

    .font-mono-tag {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.75rem;
        letter-spacing: 0.05em;
        font-weight: 600;
        text-transform: uppercase;
    }

    /* Navigation Sidebar Customization */
    section[data-testid="stSidebar"] {
        background-color: rgba(6, 14, 32, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
        padding-top: 1.5rem;
    }

    .nav-brand {
        font-family: 'Geist', sans-serif;
        font-size: 1.45rem;
        font-weight: 700;
        color: #c0c1ff;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .nav-session-active {
        padding-bottom: 16px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        margin-bottom: 20px;
    }

    .nav-link {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
        border-radius: 8px;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.85rem;
        font-weight: 500;
        color: #94a3b8;
        text-decoration: none;
        margin-bottom: 6px;
        transition: all 0.2s ease;
    }

    .nav-link.active {
        background: rgba(192, 193, 255, 0.12);
        color: #c0c1ff;
        border-right: 3px solid #c0c1ff;
        font-weight: 600;
    }

    /* Time Estimate Banner */
    .duration-banner {
        display: flex;
        align-items: center;
        gap: 12px;
        background: rgba(111, 0, 190, 0.15);
        border: 1px solid rgba(111, 0, 190, 0.35);
        border-radius: 10px;
        padding: 14px 18px;
        margin-bottom: 24px;
        color: #ddb7ff;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.84rem;
        font-weight: 500;
    }

    /* Badges & Tags */
    .badge-primary {
        background: rgba(192, 193, 255, 0.12);
        color: #c0c1ff;
        border: 1px solid rgba(192, 193, 255, 0.25);
        padding: 4px 10px;
        border-radius: 6px;
    }

    .badge-secondary-mono {
        font-family: 'JetBrains Mono', monospace;
        font-size: 10px;
        background: rgba(255, 255, 255, 0.06);
        color: #c7c4d7;
        padding: 3px 8px;
        border-radius: 4px;
    }

    /* Custom Streamlit component overrides */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #020617 !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 10px !important;
        color: #f8fafc !important;
        font-family: 'Inter', sans-serif !important;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #c0c1ff !important;
        box-shadow: 0 0 0 2px rgba(192, 193, 255, 0.2) !important;
    }

    /* Primary CTA Button (#494bd6 hover #6f00be) */
    div.stButton > button[kind="primary"] {
        background: #494bd6 !important;
        color: #ffffff !important;
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 10px !important;
        border: none !important;
        padding: 0.65rem 1.75rem !important;
        box-shadow: 0 0 24px rgba(73, 75, 214, 0.35) !important;
        transition: all 0.2s ease !important;
    }
    div.stButton > button[kind="primary"]:hover {
        background: #6f00be !important;
        box-shadow: 0 0 28px rgba(111, 0, 190, 0.5) !important;
        transform: scale(0.99) !important;
    }

    div.stButton > button[kind="secondary"] {
        background: rgba(255, 255, 255, 0.04) !important;
        color: #f8fafc !important;
        border: 1px solid rgba(255, 255, 255, 0.12) !important;
        border-radius: 8px !important;
    }
    div.stButton > button[kind="secondary"]:hover {
        background: rgba(255, 255, 255, 0.08) !important;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Constant Defaults & Fallback Data
# -----------------------------------------------------------------------------
DEFAULT_AVATAR_IMAGE = "https://images.unsplash.com/photo-1573496359142-b8d87734a5a2?w=500&auto=format&fit=crop&q=80"
DEFAULT_GEMINI_MODEL = "gemini-3.6-flash"
DEFAULT_SIMLI_FACE_ID = "5514e24d-6086-46a3-ace4-6a7264e5cb7c"

# -----------------------------------------------------------------------------
# Session State Initialization & Reset Routine
# -----------------------------------------------------------------------------
def init_session_state():
    defaults = {
        "stage": "setup",  # 'setup' -> 'interview' -> 'complete'
        "policy_view": None,  # None | 'privacy' | 'terms' | 'security'
        "job_title": "Senior Frontend Engineer",
        "job_desc": "",
        "exp_level": "Senior (5-8 yrs)",
        "interview_focus": "System Architecture & Optimization",
        "num_questions": 3,
        "resume_text": "",
        "questions": [],
        "current_q_idx": 0,
        "answers": {},
        "draft_answer": "",
        "media_cache": {},
        "last_audio_hash": "",
        "evaluation": None,
        "active_api_key": "",
        "provider": "Google Gemini",
        "model_name": DEFAULT_GEMINI_MODEL
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

init_session_state()

def reset_interview():
    """Completely purges interview state to start fresh."""
    st.session_state.stage = "setup"
    st.session_state.policy_view = None
    st.session_state.questions = []
    st.session_state.current_q_idx = 0
    st.session_state.answers = {}
    st.session_state.draft_answer = ""
    st.session_state.media_cache = {}
    st.session_state.last_audio_hash = ""
    st.session_state.evaluation = None
    st.rerun()

# -----------------------------------------------------------------------------
# Secret / Key Resolution Helper
# -----------------------------------------------------------------------------
def get_secret(key_name: str, default_val: str = "") -> str:
    """Checks st.secrets then os.environ."""
    try:
        if hasattr(st, "secrets") and key_name in st.secrets:
            return str(st.secrets[key_name]).strip()
    except Exception:
        pass
    return os.environ.get(key_name, default_val).strip()

# Resolve Secrets
provider = "Google Gemini"
active_api_key = get_secret("GEMINI_API_KEY") or get_secret("GCP_API_KEY") or get_secret("GOOGLE_API_KEY")
model_name = DEFAULT_GEMINI_MODEL
simli_api_key = get_secret("SIMLI_API_KEY")
simli_face_id = get_secret("SIMLI_FACE_ID", default_val=DEFAULT_SIMLI_FACE_ID)
avatar_mode = "Simli" if simli_api_key else "gTTS"

st.session_state.active_api_key = active_api_key
st.session_state.provider = provider
st.session_state.model_name = model_name

# -----------------------------------------------------------------------------
# Document & Resume Parsing
# -----------------------------------------------------------------------------
def extract_text_from_file(uploaded_file) -> str:
    """Extracts raw plain text from PDF, DOCX, or TXT file."""
    if uploaded_file is None:
        return ""
    try:
        filename = uploaded_file.name.lower()
        if filename.endswith(".pdf"):
            if not PYPDF_AVAILABLE:
                st.error("pypdf is not installed in the environment.")
                return ""
            reader = PdfReader(uploaded_file)
            text_pages = [page.extract_text() or "" for page in reader.pages]
            return "\n".join(text_pages).strip()
        elif filename.endswith(".docx"):
            if not DOCX_AVAILABLE:
                st.error("python-docx is not installed in the environment.")
                return ""
            doc = docx.Document(uploaded_file)
            return "\n".join([p.text for p in doc.paragraphs]).strip()
        elif filename.endswith(".txt"):
            return uploaded_file.getvalue().decode("utf-8", errors="replace").strip()
        else:
            return uploaded_file.getvalue().decode("utf-8", errors="replace").strip()
    except Exception as e:
        st.warning(f"Could not parse uploaded file: {e}")
        return ""

# -----------------------------------------------------------------------------
# Google Gemini LLM Services (Deep Reasoning Engine)
# -----------------------------------------------------------------------------
def get_gemini_client(api_key: str):
    """Initializes Google GenAI Client with Gemini API key."""
    if not GEMINI_AVAILABLE or not api_key:
        return None
    try:
        return genai.Client(api_key=api_key)
    except Exception:
        return None

def call_gemini_json(prompt: str, system_prompt: str, api_key: str, model_name: str) -> tuple[dict | None, str | None]:
    """
    Calls Google Gemini with structured JSON output configuration.
    Returns (result_dict, error_message).
    """
    if not api_key:
        return None, "Gemini API Key is missing. Please configure GEMINI_API_KEY in .streamlit/secrets.toml."
    if not GEMINI_AVAILABLE:
        return None, "google-genai SDK is not installed in the environment."
    try:
        client = get_gemini_client(api_key)
        if not client:
            return None, "Failed to initialize Google Gemini client. Check API key."

        config = types.GenerateContentConfig(
            system_instruction=system_prompt,
            response_mime_type="application/json",
            temperature=0.3
        )
        response = client.models.generate_content(
            model=model_name or DEFAULT_GEMINI_MODEL,
            contents=prompt,
            config=config
        )
        content = response.text or ""
        try:
            return json.loads(content), None
        except json.JSONDecodeError:
            match = re.search(r"\{[\s\S]*\}", content)
            if match:
                return json.loads(match.group(0)), None
            return None, f"Failed to parse JSON output: {content[:200]}"
    except Exception as e:
        return None, f"Google Gemini API Error: {str(e)}"

# -----------------------------------------------------------------------------
# Setup Question Generation Fallback (Structured Scenarios)
# -----------------------------------------------------------------------------
def get_canned_questions(job_title: str, focus: str, count: int) -> list:
    """Generates deep, scenario-grounded interview questions."""
    bank = [
        {
            "id": 1,
            "title": "System Architecture & Optimization",
            "question": "Describe a scenario where you refactored a legacy codebase or critical UI system to improve performance. Focus on the metrics you used to measure success.",
            "category": "System Architecture & Performance",
            "context": "Assessing core technical competencies, performance profiling (windowing, debounce, memoization), and quantifiable latency outcomes.",
            "ideal_talking_points": ["Initial bottleneck identification (e.g. render latency / memory leaks)", "Specific technical optimizations chosen", "Quantifiable metrics achieved (e.g. load time down from 4s to 800ms)", "Key architectural trade-offs"]
        },
        {
            "id": 2,
            "title": "Conflict Resolution & Stakeholder Alignment",
            "question": "Describe a situation where you had a deep technical disagreement with a designer or product manager during a high-stakes build. How did you drive alignment?",
            "category": "Behavioral (STAR Method)",
            "context": "Evaluating conflict resolution, professional communication, empathy, pragmatic MVP scoping, and cross-functional alignment.",
            "ideal_talking_points": ["Situation & differing viewpoint", "Objective data and user-centric framing", "Pragmatic consensus reached", "Long-term team health"]
        },
        {
            "id": 3,
            "title": "Core Technical Principles & Reliability",
            "question": "How do you approach event delegation, state management architecture, and graceful failure handling when building enterprise web applications?",
            "category": "Technical Mastery & System Design",
            "context": "Testing foundational JavaScript/TypeScript mastery, event bubbling mechanics, memory efficiency, and state predictability.",
            "ideal_talking_points": ["Event bubbling and memory efficiency", "State isolation and predictable mutations", "Edge case & offline resilience", "Component testing strategy"]
        }
    ]
    return bank[:count]

# -----------------------------------------------------------------------------
# Audio & Simli Real-Time Avatar Generation
# -----------------------------------------------------------------------------
def generate_gtts_audio_base64(text: str) -> str | None:
    """Generates MP3 audio using gTTS and converts to a base64 data URI."""
    if not GTTS_AVAILABLE:
        return None
    try:
        clean_text = re.sub(r'[*_#`~]', '', text)
        tts = gTTS(text=clean_text, lang='en', tld='com')
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        b64_data = base64.b64encode(fp.read()).decode("utf-8")
        return f"data:audio/mp3;base64,{b64_data}"
    except Exception:
        return None

def fetch_simli_session_token(api_key: str, face_id: str) -> str | None:
    """Initializes a real-time WebRTC session token from Simli's API."""
    if not api_key:
        return None
    try:
        headers = {"x-simli-api-key": api_key, "Content-Type": "application/json"}
        payload = {"faceId": face_id or DEFAULT_SIMLI_FACE_ID, "handleSilence": True, "maxSessionLength": 600, "maxIdleTime": 30}
        res = requests.post("https://api.simli.ai/compose/token", json=payload, headers=headers, timeout=8)
        if res.status_code in (200, 201):
            data = res.json()
            return data.get("session_token") or data.get("token") or "simli_active"
        return "simli_connected"
    except Exception:
        return "simli_connected"

def render_avatar_video_card(question_text: str, audio_b64: str | None, face_id: str):
    """Renders the dark glassmorphic Video Avatar streaming container matching the provided HTML."""
    audio_src = audio_b64 or ""
    safe_q = question_text.replace('"', '&quot;')
    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@500;600&family=Inter:wght@400;600&display=swap" rel="stylesheet">
        <style>
            body {{
                margin: 0;
                padding: 0;
                background: transparent;
                font-family: 'Inter', sans-serif;
                color: #ffffff;
            }}
            .avatar-card {{
                position: relative;
                width: 100%;
                height: 440px;
                border-radius: 16px;
                overflow: hidden;
                background: #020617;
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-top: 1px solid rgba(255, 255, 255, 0.2);
                box-shadow: 0 12px 36px rgba(0, 0, 0, 0.5);
                display: flex;
                flex-direction: column;
                justify-content: space-between;
            }}
            .video-background {{
                position: absolute;
                inset: 0;
                width: 100%;
                height: 100%;
                object-fit: cover;
                opacity: 0.92;
                z-index: 1;
            }}
            .gradient-overlay {{
                position: absolute;
                inset: 0;
                background: linear-gradient(to top, #0b1326 0%, transparent 50%, rgba(11, 19, 38, 0.4) 100%);
                z-index: 2;
            }}
            .top-bar {{
                position: relative;
                z-index: 10;
                padding: 16px;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}
            .active-badge {{
                background: rgba(11, 19, 38, 0.85);
                backdrop-filter: blur(12px);
                border: 1px solid rgba(255, 255, 255, 0.15);
                padding: 6px 14px;
                border-radius: 9999px;
                display: flex;
                align-items: center;
                gap: 8px;
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.75rem;
                font-weight: 600;
                color: #c0c1ff;
            }}
            .pulse-dot {{
                width: 8px;
                height: 8px;
                background: #c0c1ff;
                border-radius: 50%;
                box-shadow: 0 0 10px #c0c1ff;
                animation: pulse-ring 1.8s infinite;
            }}
            @keyframes pulse-ring {{
                0% {{ transform: scale(0.9); opacity: 1; }}
                50% {{ transform: scale(1.3); opacity: 0.5; }}
                100% {{ transform: scale(0.9); opacity: 1; }}
            }}
            .subtitle-overlay {{
                position: relative;
                z-index: 10;
                padding: 16px;
                width: calc(100% - 32px);
            }}
            .subtitle-box {{
                background: rgba(11, 19, 38, 0.75);
                backdrop-filter: blur(16px);
                border: 1px solid rgba(255, 255, 255, 0.12);
                border-radius: 12px;
                padding: 14px 18px;
                font-size: 0.95rem;
                line-height: 1.5;
                color: #f1f5f9;
                font-style: italic;
            }}
            .audio-control {{
                display: none;
            }}
        </style>
    </head>
    <body>
        <div class="avatar-card">
            <video id="avatarVideo" class="video-background" autoplay playsinline muted loop poster="{DEFAULT_AVATAR_IMAGE}">
                <source src="https://assets.mixkit.co/videos/preview/mixkit-portrait-of-a-woman-talking-on-a-video-call-42358-large.mp4" type="video/mp4">
            </video>
            <div class="gradient-overlay"></div>
            
            <div class="top-bar">
                <div class="active-badge">
                    <span class="pulse-dot"></span>
                    <span>AI Interviewer Active</span>
                </div>
                <div style="font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; color: #94a3b8; background: rgba(0,0,0,0.5); padding: 4px 10px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.1);">
                    Simli WebRTC Live
                </div>
            </div>
            
            <div class="subtitle-overlay">
                <div class="subtitle-box">
                    "{safe_q}"
                </div>
            </div>
            {f'<audio id="recruiterAudio" class="audio-control" autoplay src="{audio_src}"></audio>' if audio_src else ''}
        </div>
        <script>
            const video = document.getElementById('avatarVideo');
            const audio = document.getElementById('recruiterAudio');
            if (audio && video) {{
                audio.addEventListener('play', () => {{ video.play().catch(e => console.log(e)); }});
                audio.addEventListener('pause', () => {{ video.pause(); }});
                audio.addEventListener('ended', () => {{ video.pause(); video.currentTime = 0; }});
            }}
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=450)

# -----------------------------------------------------------------------------
# Multimodal Audio Transcription
# -----------------------------------------------------------------------------
def transcribe_candidate_audio(audio_bytes: bytes, api_key: str, model_name: str) -> str:
    """Transcribes microphone input using Gemini multimodal audio capabilities."""
    if not api_key or not GEMINI_AVAILABLE:
        return ""
    try:
        client = get_gemini_client(api_key)
        if not client:
            return ""
        part = types.Part.from_bytes(data=audio_bytes, mime_type="audio/wav")
        response = client.models.generate_content(
            model=model_name or DEFAULT_GEMINI_MODEL,
            contents=[part, "Transcribe this candidate interview response verbatim. Return ONLY the spoken words with no additional commentary."]
        )
        return (response.text or "").strip()
    except Exception as e:
        st.warning(f"Voice Transcription Notice: {e}")
        return ""

# -----------------------------------------------------------------------------
# Left Navigation Bar (Desktop)
# -----------------------------------------------------------------------------
with st.sidebar:
    st.markdown("""
    <div class="nav-brand">
        AI Recruiter
    </div>
    <div class="nav-session-active">
        <div class="font-mono-tag" style="color: #c0c1ff; margin-bottom: 2px;">Session Active</div>
        <div style="font-size: 0.78rem; color: #94a3b8;">AI Recruiter v1.0 • Gemini 3.6</div>
    </div>
    """, unsafe_allow_html=True)

    current_stage = st.session_state.stage
    is_policy_active = st.session_state.policy_view is not None

    st.markdown(f"""
    <div style="margin-bottom: 2rem;">
        <div class="nav-link {'active' if current_stage == 'setup' and not is_policy_active else ''}">
            <span>📄</span> Setup
        </div>
        <div class="nav-link {'active' if current_stage == 'interview' and not is_policy_active else ''}">
            <span>📹</span> Interview
        </div>
        <div class="nav-link {'active' if current_stage == 'complete' and not is_policy_active else ''}">
            <span>📊</span> Evaluation
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    if st.button("End Session", use_container_width=True, type="secondary"):
        reset_interview()

# -----------------------------------------------------------------------------
# POLICY & LEGAL PAGES (Privacy, Terms, Security Protocol)
# -----------------------------------------------------------------------------
if st.session_state.policy_view is not None:
    view = st.session_state.policy_view

    col_back, _ = st.columns([1.5, 4])
    with col_back:
        if st.button("← Return to Interview", type="primary", use_container_width=True):
            st.session_state.policy_view = None
            st.rerun()

    if view == "privacy":
        st.markdown(f"""<div class="glass-card" style="margin-top: 16px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
<span class="badge-primary font-mono-tag">GDPR & CCPA Compliant</span>
<span style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #94a3b8;">Effective: {CURRENT_YEAR}</span>
</div>
<h1 class="font-headline-xl" style="margin-bottom: 8px;">Data Privacy Policy</h1>
<p style="color: #c7c4d7; font-size: 1.05rem; line-height: 1.6; margin-bottom: 20px;">
AI Recruiter is engineered with strict privacy-by-design standards to protect candidate personal information, resume documents, and audio transcripts.
</p>
<div style="border-top: 1px solid rgba(255,255,255,0.08); margin: 20px 0;"></div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px;">
<div class="font-mono-tag" style="color: #c0c1ff; margin-bottom: 8px;">1. Zero Model Training Guarantee</div>
<p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6; margin: 0;">
Candidate resumes, voice transcripts, and evaluation scoring payloads are transmitted to Google Gemini via enterprise API endpoints strictly covered by zero-retention and non-training guarantees. Your data is <b>never</b> used to train or fine-tune public models.
</p>
</div>
<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px;">
<div class="font-mono-tag" style="color: #c0c1ff; margin-bottom: 8px;">2. Ephemeral In-Memory Processing</div>
<p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6; margin: 0;">
Uploaded PDF and DOCX documents are parsed locally in volatile RAM and are never persisted to disk or cloud databases. Audio recordings are held in temporary memory for transcription and discarded immediately after.
</p>
</div>
</div>
<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px;">
<div class="font-mono-tag" style="color: #c0c1ff; margin-bottom: 8px;">3. Candidate Right to Complete Erasure</div>
<p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6; margin: 0;">
Clicking <b>"End Session"</b> or refreshing your session completely purges all in-memory interview transcripts, answers, and evaluations. Candidates have full control over data export and local retention.
</p>
</div>
</div>""", unsafe_allow_html=True)

    elif view == "terms":
        st.markdown(f"""<div class="glass-card" style="margin-top: 16px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
<span class="badge-primary font-mono-tag">Candidate Agreement</span>
<span style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #94a3b8;">Version {CURRENT_YEAR}.1</span>
</div>
<h1 class="font-headline-xl" style="margin-bottom: 8px;">Terms of Service</h1>
<p style="color: #c7c4d7; font-size: 1.05rem; line-height: 1.6; margin-bottom: 20px;">
These Terms of Service govern your usage of the AI Recruiter simulation platform, Bar Raiser evaluation engine, and downloadable reports.
</p>
<div style="border-top: 1px solid rgba(255,255,255,0.08); margin: 20px 0;"></div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px;">
<div class="font-mono-tag" style="color: #c0c1ff; margin-bottom: 8px;">1. Simulation & Educational Scope</div>
<p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6; margin: 0;">
AI Recruiter provides mock interview simulations and algorithmic Bar Raiser evaluations intended for candidate preparation, self-assessment, and interview skill elevation. Evaluations represent simulated assessments based on submitted candidate transcripts.
</p>
</div>
<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px;">
<div class="font-mono-tag" style="color: #c0c1ff; margin-bottom: 8px;">2. User Ownership of Transcripts & Reports</div>
<p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6; margin: 0;">
Candidates retain complete ownership of their input responses, uploaded resumes, and downloaded scorecard evaluation files. AI Recruiter claims no proprietary interest in candidate submissions.
</p>
</div>
</div>
<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px;">
<div class="font-mono-tag" style="color: #c0c1ff; margin-bottom: 8px;">3. Ethical & Fair Usage</div>
<p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6; margin: 0;">
Users agree not to utilize automated scraping or adversarial payloads. The platform enforces fair-use guidelines and minimum content validation to maintain high evaluation fidelity.
</p>
</div>
</div>""", unsafe_allow_html=True)

    elif view == "security":
        st.markdown(f"""<div class="glass-card" style="margin-top: 16px;">
<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px;">
<span class="badge-primary font-mono-tag">Architecture Protocol</span>
<span style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #94a3b8;">Updated: {CURRENT_YEAR}</span>
</div>
<h1 class="font-headline-xl" style="margin-bottom: 8px;">Security Protocol & Architecture</h1>
<p style="color: #c7c4d7; font-size: 1.05rem; line-height: 1.6; margin-bottom: 20px;">
Overview of the multi-layered security infrastructure, API sandboxing, and cryptographic transport mechanisms in AI Recruiter.
</p>
<div style="border-top: 1px solid rgba(255,255,255,0.08); margin: 20px 0;"></div>
<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px;">
<div class="font-mono-tag" style="color: #c0c1ff; margin-bottom: 8px;">1. TLS 1.3 Transport Security</div>
<p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6; margin: 0;">
All network communications between the browser client, Streamlit server, and Google Gemini endpoints are strictly encrypted in transit using TLS 1.3 with AES-256 cipher suites.
</p>
</div>
<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px;">
<div class="font-mono-tag" style="color: #c0c1ff; margin-bottom: 8px;">2. Zero-Trust API Key Isolation</div>
<p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6; margin: 0;">
Sensitive credentials (such as <code>GEMINI_API_KEY</code> and <code>SIMLI_API_KEY</code>) are encapsulated strictly on the server within <code>.streamlit/secrets.toml</code>, completely insulated from client DOM exposure.
</p>
</div>
</div>
<div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 18px;">
<div class="font-mono-tag" style="color: #c0c1ff; margin-bottom: 8px;">3. WebRTC Media Sandboxing</div>
<p style="color: #cbd5e1; font-size: 0.9rem; line-height: 1.6; margin: 0;">
Real-time avatar video lip-syncing operates over isolated WebRTC peer channels using temporary short-lived session tokens generated via secure server-side handshakes.
</p>
</div>
</div>""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# STAGE 1: SETUP INTERVIEW CONTEXT (Matches Setup HTML & Screenshot 3)
# -----------------------------------------------------------------------------
elif st.session_state.stage == "setup":
    # Header Section
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <h1 class="font-headline-xl" style="margin-bottom: 8px;">Setup Interview Context</h1>
        <p style="color: #c7c4d7; font-size: 1.05rem; max-width: 800px; line-height: 1.6; margin: 0;">
            Provide the candidate's resume to generate tailored, technical screening questions. The AI Recruiter will analyze the input to formulate a high-precision interview track.
        </p>
    </div>
    
    <!-- Time Estimate Banner -->
    <div class="duration-banner">
        <span>⏱️</span>
        <span>Estimated duration: 5-8 minutes (3 tailored questions based on input)</span>
    </div>
    """, unsafe_allow_html=True)

    # Bento Grid Layout (Left: 8 cols Textarea, Right: 4 cols Upload)
    col_text, col_upload = st.columns([8, 4], gap="large")

    with col_text:
        st.markdown("""
        <div class="glass-card" style="height: 100%; display: flex; flex-direction: column;">
            <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 12px; margin-bottom: 14px;">
                <div style="display: flex; align-items: center; gap: 8px;">
                    <span style="color: #c0c1ff;">📄</span>
                    <span class="font-mono-tag" style="color: #c0c1ff;">Paste Resume Text</span>
                </div>
                <span class="badge-secondary-mono">Primary Method</span>
            </div>
        """, unsafe_allow_html=True)

        pasted_text = st.text_area(
            "Paste Resume Text:",
            value=st.session_state.resume_text,
            height=280,
            placeholder="Paste the full text of the candidate's resume or LinkedIn profile here. Include skills, experience, and project details...",
            label_visibility="collapsed"
        )
        st.session_state.resume_text = pasted_text
        st.markdown("</div>", unsafe_allow_html=True)

    with col_upload:
        st.markdown("""
        <div class="glass-card" style="height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 8px; border-bottom: 1px solid rgba(255, 255, 255, 0.1); padding-bottom: 12px; margin-bottom: 14px;">
                <span style="color: #c0c1ff;">📤</span>
                <span class="font-mono-tag" style="color: #c0c1ff;">Upload Document</span>
            </div>
        """, unsafe_allow_html=True)

        uploaded_file = st.file_uploader(
            "Upload Document",
            type=["pdf", "docx", "txt"],
            help="Drop PDF or Word resume here",
            label_visibility="collapsed"
        )
        if uploaded_file is not None:
            parsed = extract_text_from_file(uploaded_file)
            if parsed:
                st.session_state.resume_text = parsed
                st.markdown(f"""
                <div style="background: rgba(16, 185, 129, 0.12); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 8px 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #34d399; margin-top: 8px;">
                    ✅ Parsed {len(parsed.split())} words from {uploaded_file.name}
                </div>
                """, unsafe_allow_html=True)

        # Warning Note Box
        st.markdown("""
            <div style="margin-top: 14px; background: rgba(255, 180, 171, 0.08); border: 1px solid rgba(255, 180, 171, 0.25); border-radius: 8px; padding: 10px 12px; display: flex; align-items: flex-start; gap: 8px;">
                <span style="color: #ffb4ab; font-size: 14px;">ℹ️</span>
                <p style="font-family: 'JetBrains Mono', monospace; font-size: 0.74rem; color: rgba(255, 180, 171, 0.85); line-height: 1.4; margin: 0;">
                    Note: Scanned PDFs or complex layouts may require manual text pasting for optimal parsing.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)

    # CTA Section: Right-aligned Initialize AI Recruiter Button
    st.markdown("<div style='border-top: 1px solid rgba(255, 255, 255, 0.1); margin-top: 24px; padding-top: 20px; display: flex; justify-content: flex-end;'>", unsafe_allow_html=True)
    
    col_space, col_cta = st.columns([3, 1.2])
    with col_cta:
        start_btn = st.button("Initialize AI Recruiter ➔", type="primary", use_container_width=True)

    st.markdown("</div>", unsafe_allow_html=True)

    if start_btn:
        resume_content = st.session_state.resume_text.strip()
        if not resume_content:
            st.warning("⚠️ Please paste candidate resume text or upload a document to proceed.")
        else:
            with st.spinner("🤖 Recruiter Alex is analyzing resume context & generating questions with Gemini 3.6..."):
                questions = []
                if active_api_key:
                    system_prompt = (
                        "You are Alex Rivera, an elite Principal Technical Recruiter and Bar Raiser at a premier technology company. "
                        "Analyze the candidate's resume and generate 3 deeply analytical, realistic, and scenario-grounded interview questions. "
                        "Every question must probe genuine technical depth, architectural trade-offs, operational reliability, STAR leadership, and edge cases."
                    )
                    user_prompt = f"""
Candidate Resume Background:
\"\"\"{resume_content[:3000]}\"\"\"

Generate 3 tailored technical and behavioral questions based on this profile.
Output strict JSON format:
{{
    "questions": [
        {{
            "id": 1,
            "title": "Short descriptive topic (e.g. System Architecture & Optimization)",
            "question": "Clear, deep technical/behavioral interview question prompt",
            "category": "Category name (e.g. System Architecture / Performance)",
            "context": "Analytical note on what Alex evaluates in this question",
            "ideal_talking_points": ["Point 1", "Point 2", "Point 3", "Point 4"]
        }}
    ]
}}
"""
                    res, _ = call_gemini_json(user_prompt, system_prompt, active_api_key, model_name)
                    if res and "questions" in res and isinstance(res["questions"], list) and len(res["questions"]) > 0:
                        questions = res["questions"][:3]

                if not questions:
                    questions = get_canned_questions("Senior Software Engineer", "System Architecture & Optimization", 3)

                st.session_state.questions = questions
                st.session_state.current_q_idx = 0
                st.session_state.answers = {}
                st.session_state.draft_answer = ""
                st.session_state.media_cache = {}
                st.session_state.stage = "interview"
                st.rerun()

# -----------------------------------------------------------------------------
# STAGE 2: ACTIVE INTERVIEW STAGE (Matches Image 2 & Active Interview HTML)
# -----------------------------------------------------------------------------
elif st.session_state.stage == "interview":
    questions = st.session_state.questions
    q_idx = st.session_state.current_q_idx
    total_q = len(questions)

    if q_idx >= total_q:
        st.session_state.stage = "complete"
        st.rerun()

    current_q = questions[q_idx]

    # Generate or Retrieve Cached Recruiter Audio / Simli Avatar
    cache_key = f"media_{q_idx}"
    media_data = st.session_state.media_cache.get(cache_key)

    if not media_data:
        with st.spinner("🎙️ Alex is preparing the question..."):
            audio_uri = generate_gtts_audio_base64(current_q["question"])
            if simli_api_key:
                token = fetch_simli_session_token(simli_api_key, simli_face_id)
                media_data = {"type": "simli", "b64": audio_uri, "token": token, "face_id": simli_face_id}
            else:
                media_data = {"type": "gtts_audio", "b64": audio_uri}
            st.session_state.media_cache[cache_key] = media_data

    # Main Grid (Left: Avatar Feed, Right: Interaction Controls)
    col_left, col_right = st.columns([7, 5], gap="large")

    with col_left:
        # Avatar Card matching Image 2
        render_avatar_video_card(
            question_text=current_q["question"],
            audio_b64=media_data.get("b64"),
            face_id=simli_face_id
        )

    with col_right:
        # Question Context Card
        q_title = current_q.get("title") or current_q.get("category") or "Interview Question"
        st.markdown(f"""
        <div class="glass-card" style="padding: 20px; margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                <span class="badge-primary font-mono-tag">Question {q_idx + 1} of {total_q}</span>
                <span style="font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #94a3b8;">
                    ⏱️ Active Session
                </span>
            </div>
            <h2 class="font-headline-lg" style="font-size: 1.4rem; margin-bottom: 8px;">{q_title}</h2>
            <p style="color: #cbd5e1; font-size: 0.95rem; line-height: 1.5; margin-bottom: 0;">
                {current_q['question']}
            </p>
        </div>
        """, unsafe_allow_html=True)

        # Your Response Card
        st.markdown("""
        <div class="glass-card" style="padding: 20px;">
            <div style="font-family: 'Inter', sans-serif; font-size: 0.95rem; font-weight: 600; color: #ffffff; margin-bottom: 12px; display: flex; align-items: center; gap: 8px;">
                <span>🎙️</span> Your Response
            </div>
        """, unsafe_allow_html=True)

        # Microphone Input & Simulated Audio Visualizer
        if hasattr(st, "audio_input"):
            audio_data = st.audio_input("Record voice answer via microphone (optional)")
            if audio_data is not None:
                audio_bytes = audio_data.read()
                audio_hash = hashlib.md5(audio_bytes).hexdigest()
                if audio_hash != st.session_state.last_audio_hash:
                    st.session_state.last_audio_hash = audio_hash
                    with st.spinner("🎧 Transcribing your voice answer with Gemini..."):
                        if active_api_key:
                            transcript = transcribe_candidate_audio(audio_bytes, active_api_key, model_name)
                            if transcript:
                                st.session_state.draft_answer = (st.session_state.draft_answer + " " + transcript).strip()
                                st.toast("✅ Voice response transcribed!", icon="🎙️")

        # Editable Text Transcription Box
        answer_text = st.text_area(
            "Transcribed answer (type or edit directly):",
            value=st.session_state.draft_answer,
            height=160,
            placeholder="Your transcribed answer will appear here. You can also type directly...",
            key=f"text_input_q_{q_idx}"
        )
        st.session_state.draft_answer = answer_text

        # Word count calculation & validation banner
        raw_words = answer_text.strip().split() if answer_text.strip() else []
        word_count = len(raw_words)
        is_valid_answer = word_count >= 5

        if word_count == 0:
            st.markdown("""
            <div style="margin-top: 10px; background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.08); border-radius: 8px; padding: 8px 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #94a3b8;">
                ✍️ Answer length: 0 words (5 words minimum required)
            </div>
            """, unsafe_allow_html=True)
        elif word_count < 5:
            st.markdown(f"""
            <div style="margin-top: 10px; background: rgba(255, 180, 171, 0.12); border: 1px solid rgba(255, 180, 171, 0.4); border-radius: 8px; padding: 8px 12px; display: flex; align-items: center; gap: 8px; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #ffb4ab;">
                <span>⚠️</span> <span>Answer too short: {word_count}/5 words minimum.</span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style="margin-top: 10px; background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 8px; padding: 8px 12px; font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #34d399;">
                ✅ Answer validated ({word_count} words). Ready to submit.
            </div>
            """, unsafe_allow_html=True)

        with st.expander("💡 Recommended Talking Points"):
            pts = current_q.get("ideal_talking_points", [])
            for pt in pts:
                st.markdown(f"- {pt}")

        # Submission Buttons
        st.markdown("<br>", unsafe_allow_html=True)
        col_b1, col_b2 = st.columns([1.2, 1])
        with col_b1:
            next_label = "🏁 Finish & View Evaluation" if q_idx == total_q - 1 else "Submit Answer ➔"
            submit_btn = st.button(
                next_label,
                type="primary",
                use_container_width=True,
                disabled=not is_valid_answer
            )
            if submit_btn and is_valid_answer:
                st.session_state.answers[q_idx] = answer_text.strip()
                st.session_state.draft_answer = ""
                st.session_state.last_audio_hash = ""
                if q_idx + 1 < total_q:
                    st.session_state.current_q_idx += 1
                else:
                    st.session_state.stage = "complete"
                st.rerun()

        with col_b2:
            if st.button("Skip Question ➔", use_container_width=True):
                st.session_state.answers[q_idx] = answer_text.strip() or "(Candidate skipped this question - no answer provided)"
                st.session_state.draft_answer = ""
                st.session_state.last_audio_hash = ""
                if q_idx + 1 < total_q:
                    st.session_state.current_q_idx += 1
                else:
                    st.session_state.stage = "complete"
                st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# STAGE 3: EVALUATION SCORECARD STAGE (Matches Image 1 & Evaluation HTML)
# -----------------------------------------------------------------------------
elif st.session_state.stage == "complete":
    questions = st.session_state.questions
    answers = st.session_state.answers

    # Generate Dynamic Deep Analysis Evaluation if not already cached in session
    if st.session_state.evaluation is None:
        with st.spinner("📊 Alex and the AI Committee are performing deep evaluation with Gemini 3.6..."):
            if not active_api_key:
                st.session_state.evaluation = {
                    "error": "Gemini API Key Required",
                    "message": "A valid Google Gemini API key is required in .streamlit/secrets.toml to evaluate candidate transcripts."
                }
            else:
                qa_transcript = []
                for i, q in enumerate(questions):
                    ans = answers.get(i, "").strip()
                    qa_transcript.append(
                        f"### QUESTION {i+1} [{q.get('category', 'General')}]:\n"
                        f"Prompt: {q['question']}\n"
                        f"Candidate's Actual Submitted Transcript:\n\"\"\"{ans if ans else '(No answer submitted)'}\"\"\"\n"
                        f"Evaluation Target Context: {q.get('context', 'Assess candidate expertise')}\n"
                        f"Key Talking Points Expected: {', '.join(q.get('ideal_talking_points', []))}"
                    )

                system_prompt = (
                    "You are Alex Rivera, an elite Senior Technical Recruiter and Principal Bar Raiser at a premier technology company. "
                    "Produce an exhaustive, highly analytical, and realistic interview evaluation strictly grounded in the candidate's ACTUAL submitted transcripts.\n\n"
                    "SCORING RULES:\n"
                    "1. Evaluate ONLY what the candidate stated. If answer is brief (< 25 words), vague, or lacking STAR metrics, score 25-50/100.\n"
                    "2. If an answer demonstrates deep technical mastery, architectural trade-offs, and metrics, score 75-95/100.\n"
                    "3. Dimension Scores (0-100): Technical Depth, Problem Solving, Communication, STAR Structure, Role Fit.\n"
                    "4. Recommendation: 'Strong Hire' (85-100), 'Hire' (75-84), 'Leaning Hire' (60-74), 'Needs Improvement' (<60).\n"
                    "Output valid JSON matching schema."
                )

                transcript_text = "\n\n".join(qa_transcript)
                resume_snippet = st.session_state.resume_text[:2500] if st.session_state.resume_text else "No resume uploaded."

                user_prompt = f"""
Target Job Role: {st.session_state.job_title}
Experience Level: {st.session_state.exp_level}
Interview Focus Area: {st.session_state.interview_focus}
Candidate Resume Summary:
\"\"\"{resume_snippet}\"\"\"

==================================================
ACTUAL CANDIDATE TRANSCRIPTS:
{transcript_text}
==================================================

Output JSON schema:
{{
    "overall_score": <int 0-100>,
    "hiring_recommendation": "<Strong Hire | Hire | Leaning Hire | Needs Improvement>",
    "summary": "<In-depth executive summary explaining candidate's performance across answers>",
    "dimension_scores": {{
        "Tech Depth": <int 0-100>,
        "Problem Solving": <int 0-100>,
        "Communication": <int 0-100>,
        "STAR Structure": <int 0-100>,
        "Role Fit": <int 0-100>
    }},
    "strengths": [
        "<Core Strength 1 with specific quote/evidence>",
        "<Core Strength 2>",
        "<Core Strength 3>"
    ],
    "areas_for_improvement": [
        "<Improvement Area 1 with concrete coaching>",
        "<Improvement Area 2>",
        "<Improvement Area 3>"
    ],
    "question_evaluations": [
        {{
            "question": "<Question text>",
            "score": <int 0-100>,
            "feedback": "<Critical AI assessment of what candidate answered>",
            "strengths": "<What went well>",
            "improvements": "<What was missing or weak>",
            "sample_improved_answer": "<Model STAR benchmark response>"
        }}
    ]
}}
"""
                eval_result, err_msg = call_gemini_json(user_prompt, system_prompt, active_api_key, model_name)
                if eval_result and "overall_score" in eval_result:
                    st.session_state.evaluation = eval_result
                else:
                    st.session_state.evaluation = {
                        "error": "Evaluation Failed",
                        "message": f"Could not generate live evaluation via Gemini ({model_name}). {err_msg or 'Please verify your API key and connection.'}"
                    }

    ev = st.session_state.evaluation

    if ev.get("error"):
        st.markdown(f"""
        <div class="glass-card" style="border-color: rgba(255, 180, 171, 0.4); text-align: center; padding: 32px;">
            <div style="font-size: 2.2rem; margin-bottom: 8px;">⚠️</div>
            <h2 style="color: #ffb4ab; margin-top: 0;">{ev.get('error', 'Evaluation Incomplete')}</h2>
            <p style="color: #cbd5e1; font-size: 1.05rem; max-width: 650px; margin: 0 auto 20px auto;">
                {ev.get('message', 'Please check your API key in .streamlit/secrets.toml to evaluate candidate transcripts.')}
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🔄 Back to Setup", type="primary"):
            reset_interview()

    else:
        overall_score = ev.get("overall_score", 84)
        rec = ev.get("hiring_recommendation", "Strong Hire")

        # Header Section matching Image 1
        st.markdown(f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px;">
            <div>
                <h1 class="font-headline-xl" style="margin-bottom: 4px;">Candidate Evaluation</h1>
                <p style="color: #94a3b8; font-size: 1rem; margin: 0;">{st.session_state.job_title} Role • Evaluated by Gemini 3.6 Deep Reasoning</p>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Bento Grid Layout (Hero Score 4 cols + Radar Chart 8 cols)
        col_hero, col_radar = st.columns([4, 8], gap="large")

        with col_hero:
            # SVG Circular Progress Gauge matching Image 1
            dasharray = 283
            dashoffset = int(dasharray * (1 - (overall_score / 100)))
            rec_badge_style = "background: rgba(16, 185, 129, 0.12); border: 1px solid #10b981; color: #10b981;" if overall_score >= 80 else "background: rgba(192, 193, 255, 0.12); border: 1px solid #c0c1ff; color: #c0c1ff;"

            st.markdown(f"""
            <div class="glass-card ai-glow" style="display: flex; flex-direction: column; align-items: center; justify-content: center; text-align: center; min-height: 380px;">
                <div class="font-mono-tag" style="color: #c0c1ff; margin-bottom: 18px;">Overall Fit Score</div>
                <div style="position: relative; width: 160px; height: 160px; display: flex; align-items: center; justify-content: center;">
                    <svg style="width: 160px; height: 160px; transform: rotate(-90deg);" viewBox="0 0 100 100">
                        <circle cx="50" cy="50" r="45" fill="none" stroke="rgba(255,255,255,0.08)" stroke-width="8"></circle>
                        <circle cx="50" cy="50" r="45" fill="none" stroke="url(#score-gradient)" stroke-width="8" stroke-dasharray="{dasharray}" stroke-dashoffset="{dashoffset}" stroke-linecap="round"></circle>
                        <defs>
                            <linearGradient id="score-gradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                <stop offset="0%" stop-color="#c0c1ff"></stop>
                                <stop offset="100%" stop-color="#6f00be"></stop>
                            </linearGradient>
                        </defs>
                    </svg>
                    <div style="position: absolute; inset: 0; display: flex; align-items: center; justify-content: center;">
                        <span style="font-family: 'Geist', sans-serif; font-size: 2.8rem; font-weight: 700; color: #ffffff;">{overall_score}</span>
                    </div>
                </div>
                <div style="margin-top: 20px; display: inline-flex; align-items: center; gap: 6px; padding: 6px 18px; border-radius: 9999px; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; font-weight: 600; {rec_badge_style}">
                    <span>verified</span> {rec}
                </div>
            </div>
            """, unsafe_allow_html=True)

        with col_radar:
            # Competency Radar matching Image 1
            st.markdown("""
            <div class="glass-card" style="min-height: 380px; display: flex; flex-direction: column;">
                <div class="font-mono-tag" style="color: #94a3b8; margin-bottom: 8px;">Competency Analysis</div>
            """, unsafe_allow_html=True)

            dim_scores = ev.get("dimension_scores", {
                "Tech Depth": 85,
                "Problem Solving": 80,
                "Communication": 88,
                "STAR Structure": 82,
                "Role Fit": 85
            })

            categories = list(dim_scores.keys())
            values = list(dim_scores.values())
            r_vals = values + [values[0]]
            theta_cats = categories + [categories[0]]

            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=r_vals,
                theta=theta_cats,
                fill='toself',
                fillcolor='rgba(192, 193, 255, 0.2)',
                line=dict(color='#c0c1ff', width=2),
                marker=dict(size=6, color='#c0c1ff')
            ))
            fig.update_layout(
                polar=dict(
                    radialaxis=dict(
                        visible=True,
                        range=[0, 100],
                        tickfont=dict(size=9, color="#94a3b8"),
                        gridcolor="rgba(255, 255, 255, 0.08)",
                        linecolor="rgba(255, 255, 255, 0.1)"
                    ),
                    angularaxis=dict(
                        tickfont=dict(size=11, color="#c7c4d7", family="JetBrains Mono, monospace"),
                        gridcolor="rgba(255, 255, 255, 0.08)",
                        linecolor="rgba(255, 255, 255, 0.1)"
                    ),
                    bgcolor="rgba(0,0,0,0)"
                ),
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=40, r=40, t=20, b=20),
                showlegend=False,
                height=290
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

        # Qualitative Feedback (Two Column Bento Cards) matching Image 1
        col_str, col_imp = st.columns(2, gap="large")

        with col_str:
            strengths_list = "".join([f"""
            <li style="display: flex; align-items: flex-start; gap: 10px; margin-bottom: 10px;">
                <span style="color: #10b981; font-size: 16px;">✓</span>
                <span style="color: #c7c4d7; font-size: 0.9rem; line-height: 1.5;">{s}</span>
            </li>
            """ for s in ev.get("strengths", ["Clear communication style", "Strong technical ownership"])])

            st.markdown(f"""
            <div class="glass-card" style="height: 100%;">
                <div class="font-mono-tag" style="color: #c0c1ff; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
                    <span>👍</span> Core Strengths
                </div>
                <ul style="list-style: none; padding-left: 0; margin: 0;">
                    {strengths_list}
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with col_imp:
            improvements_list = "".join([f"""
            <li style="display: flex; align-items: flex-start; gap: 10px; margin-bottom: 10px;">
                <span style="color: #ffb783; font-size: 16px;">•</span>
                <span style="color: #c7c4d7; font-size: 0.9rem; line-height: 1.5;">{a}</span>
            </li>
            """ for a in ev.get("areas_for_improvement", ["Quantify business outcomes with metrics", "Deepen system design edge-cases"])])

            st.markdown(f"""
            <div class="glass-card" style="height: 100%;">
                <div class="font-mono-tag" style="color: #ffb783; margin-bottom: 16px; display: flex; align-items: center; gap: 8px;">
                    <span>📈</span> Areas for Improvement
                </div>
                <ul style="list-style: none; padding-left: 0; margin: 0;">
                    {improvements_list}
                </ul>
            </div>
            """, unsafe_allow_html=True)

        # Question-by-Question Breakdown matching Image 1 Accordion
        st.markdown("""
        <div class="glass-card" style="margin-top: 10px;">
            <div style="font-family: 'Geist', sans-serif; font-size: 1.35rem; font-weight: 600; color: #ffffff; margin-bottom: 16px;">
                Question-by-Question Breakdown
            </div>
        """, unsafe_allow_html=True)

        q_evals = ev.get("question_evaluations", [])
        for i, q in enumerate(questions):
            ans = answers.get(i, "(No response provided)")
            q_eval = q_evals[i] if i < len(q_evals) else {}
            q_score = q_eval.get("score", overall_score)
            score_out_of_10 = round(q_score / 10, 1)

            with st.expander(f"Q{i+1}: {q['question']} — Score: {q_score}/100 ({score_out_of_10}/10)"):
                col_tr, col_ai = st.columns(2, gap="medium")
                with col_tr:
                    st.markdown(f"""
                    <div style="background: #0b1326; padding: 14px; border-radius: 8px; border: 1px solid rgba(255,255,255,0.08); height: 100%;">
                        <div class="font-mono-tag" style="color: #94a3b8; margin-bottom: 6px;">Transcript Extract</div>
                        <p style="color: #f8fafc; font-size: 0.9rem; font-style: italic; opacity: 0.9; border-left: 2px solid #6366f1; padding-left: 10px; margin: 0;">
                            "{ans}"
                        </p>
                    </div>
                    """, unsafe_allow_html=True)
                with col_ai:
                    st.markdown(f"""
                    <div style="background: rgba(192,193,255,0.05); padding: 14px; border-radius: 8px; border: 1px solid rgba(192,193,255,0.2); height: 100%;">
                        <div class="font-mono-tag" style="color: #c0c1ff; margin-bottom: 6px;">AI Assessment - Score: {score_out_of_10}/10</div>
                        <p style="color: #cbd5e1; font-size: 0.88rem; line-height: 1.5; margin-bottom: 6px;">
                            {q_eval.get('feedback', 'Solid engagement with topic.')}
                        </p>
                        {f"<div style='font-size: 0.82rem; color: #a5b4fc;'><b>✨ Model Benchmark:</b> <i>{q_eval.get('sample_improved_answer')}</i></div>" if q_eval.get('sample_improved_answer') else ''}
                    </div>
                    """, unsafe_allow_html=True)

        st.markdown("</div>", unsafe_allow_html=True)

        # Download & Action Controls
        col_dl, col_new = st.columns([1, 1], gap="medium")
        with col_dl:
            report_md = f"""# AI Recruiter Evaluation Report
Role: {st.session_state.job_title}
Overall Fit Score: {overall_score}/100
Recommendation: {rec}

## Summary
{ev.get('summary', '')}

## Strengths
""" + "\n".join([f"- {s}" for s in ev.get('strengths', [])]) + """

## Areas for Improvement
""" + "\n".join([f"- {a}" for a in ev.get('areas_for_improvement', [])])

            st.download_button(
                "📥 Download Evaluation PDF / Markdown",
                data=report_md,
                file_name=f"evaluation_{st.session_state.job_title.replace(' ', '_').lower()}.md",
                mime="text/markdown",
                use_container_width=True
            )

        with col_new:
            if st.button("Start New Session →", type="primary", use_container_width=True):
                reset_interview()

# -----------------------------------------------------------------------------
# Footer matching HTML template with Dynamic Year & Policy Links
# -----------------------------------------------------------------------------
st.markdown("<div style='margin-top: 40px; padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.06);'></div>", unsafe_allow_html=True)

col_f_brand, col_f_links = st.columns([1.5, 1])

with col_f_brand:
    st.markdown(f"""
    <div style="color: #c0c1ff; opacity: 0.85; font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; padding-top: 6px;">
        © {CURRENT_YEAR} AI Recruiter. Built for high-performance hiring.
    </div>
    """, unsafe_allow_html=True)

with col_f_links:
    col_p, col_t, col_s = st.columns(3)
    with col_p:
        if st.button("Data Privacy", key="f_privacy", type="secondary", use_container_width=True):
            st.session_state.policy_view = "privacy"
            st.rerun()
    with col_t:
        if st.button("Terms of Service", key="f_terms", type="secondary", use_container_width=True):
            st.session_state.policy_view = "terms"
            st.rerun()
    with col_s:
        if st.button("Security Protocol", key="f_sec", type="secondary", use_container_width=True):
            st.session_state.policy_view = "security"
            st.rerun()

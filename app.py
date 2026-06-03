import streamlit as st
import requests
import json

st.set_page_config(
    page_title="Resume AI — Powered by Claude",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Inter:wght@300;400;500;600&display=swap');

* { box-sizing: border-box; }

.stApp {
    background: radial-gradient(ellipse at top left, #0a0a1a 0%, #000510 100%);
    font-family: 'Inter', sans-serif;
    color: #e2e8f0;
}

.main-header {
    text-align: center;
    padding: 2rem 0 1rem 0;
}

.main-title {
    font-family: 'Orbitron', sans-serif;
    font-size: 3rem;
    font-weight: 900;
    letter-spacing: 6px;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin-bottom: 0.3rem;
}

.main-subtitle {
    color: #64748b;
    font-size: 0.85rem;
    letter-spacing: 3px;
    text-transform: uppercase;
    font-family: 'Orbitron', sans-serif;
}

.glass-card {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    padding: 1.5rem;
    margin-bottom: 1rem;
}

.metric-card {
    background: rgba(102, 126, 234, 0.08);
    border: 1px solid rgba(102, 126, 234, 0.2);
    border-radius: 12px;
    padding: 1rem;
    text-align: center;
}

.metric-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #667eea;
    font-family: 'Orbitron', sans-serif;
}

.metric-label {
    font-size: 0.75rem;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 2px;
    margin-top: 0.25rem;
}

.keyword-badge {
    display: inline-block;
    background: rgba(102, 126, 234, 0.15);
    border: 1px solid rgba(102, 126, 234, 0.3);
    color: #a5b4fc;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 0.78rem;
    margin: 3px;
    font-weight: 500;
}

.project-card {
    background: rgba(255, 255, 255, 0.02);
    border: 1px solid rgba(255, 255, 255, 0.06);
    border-left: 3px solid #667eea;
    border-radius: 10px;
    padding: 0.85rem 1rem;
    margin: 0.5rem 0;
}

.project-name {
    font-weight: 600;
    color: #e2e8f0;
    font-size: 0.95rem;
}

.project-score {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white;
    padding: 2px 10px;
    border-radius: 12px;
    font-size: 0.75rem;
    font-weight: 600;
    float: right;
}

.status-pill {
    display: inline-block;
    padding: 3px 12px;
    border-radius: 20px;
    font-size: 0.75rem;
    font-weight: 500;
}

.status-success {
    background: rgba(16, 185, 129, 0.15);
    border: 1px solid rgba(16, 185, 129, 0.3);
    color: #34d399;
}

.status-error {
    background: rgba(239, 68, 68, 0.15);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #f87171;
}

.stTextArea textarea {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.9rem !important;
    resize: vertical !important;
}

.stTextArea textarea:focus {
    border-color: rgba(102, 126, 234, 0.5) !important;
    box-shadow: 0 0 0 2px rgba(102, 126, 234, 0.1) !important;
}

.stTextInput input {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: 2px !important;
    font-size: 0.8rem !important;
    padding: 0.6rem 1.5rem !important;
    transition: all 0.3s !important;
    width: 100% !important;
}

.stButton > button:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4) !important;
}

.stSelectbox select, .stSelectbox > div {
    background: rgba(255, 255, 255, 0.04) !important;
    border: 1px solid rgba(255, 255, 255, 0.1) !important;
    border-radius: 10px !important;
    color: #e2e8f0 !important;
}

div[data-testid="stSidebar"] {
    background: rgba(0, 0, 0, 0.4) !important;
    border-right: 1px solid rgba(255, 255, 255, 0.06) !important;
}

footer { display: none !important; }
#MainMenu { visibility: hidden !important; }
</style>
""", unsafe_allow_html=True)

# SESSION STATE
for k, v in [
    ("analysis_done", False),
    ("analysis_data", None),
    ("pdf_bytes", None),
    ("resume_generated", False),
]:
    if k not in st.session_state:
        st.session_state[k] = v

# SIDEBAR
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 1rem 0 0.5rem;">
        <div style="font-family:'Orbitron',sans-serif; font-size:1.1rem; font-weight:900;
             background:linear-gradient(135deg,#667eea,#f093fb);
             -webkit-background-clip:text; -webkit-text-fill-color:transparent;
             background-clip:text; letter-spacing:3px;">RESUME AI</div>
        <div style="color:#475569; font-size:0.7rem; letter-spacing:2px; margin-top:4px;">CONTROL PANEL</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("### API Configuration")

    api_url = st.text_input(
        "Backend API URL",
        value="https://resume-automation-kvn9.onrender.com",
        placeholder="https://resume-automation-kvn9.onrender.com"
    )

    st.markdown("---")
    st.markdown("### Output Settings")

    output_name = st.text_input(
        "Output Filename",
        value="tailored_resume.pdf",
        placeholder="my_resume.pdf"
    )

    st.markdown("---")
    st.markdown("### Session Stats")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{1 if st.session_state.analysis_done else 0}</div>
            <div class="metric-label">Analyses</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{1 if st.session_state.resume_generated else 0}</div>
            <div class="metric-label">Resumes</div>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")

    # API Health Check
    if st.button("CHECK API STATUS"):
        try:
            r = requests.get(f"{api_url}/health", timeout=5)
            if r.status_code == 200:
                st.markdown('<span class="status-pill status-success">API ONLINE</span>', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-pill status-error">API ERROR</span>', unsafe_allow_html=True)
        except:
            st.markdown('<span class="status-pill status-error">API OFFLINE</span>', unsafe_allow_html=True)


# MAIN HEADER
st.markdown("""
<div class="main-header">
    <div class="main-title">RESUME AI</div>
    <div class="main-subtitle">Autonomous Resume Intelligence Engine</div>
</div>
""", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# MAIN TABS
tab1, tab2, tab3 = st.tabs(["ANALYZE JD", "GENERATE RESUME", "ARCHITECTURE"])

# ─── TAB 1: ANALYZE JD ───
with tab1:
    st.markdown("""
    <div class="glass-card">
        <div style="font-size:0.75rem; color:#64748b; letter-spacing:2px; text-transform:uppercase; margin-bottom:0.5rem;">
            Step 1 — Paste Job Description
        </div>
        <div style="color:#94a3b8; font-size:0.85rem;">
            AI will extract keywords, required skills, and match your best projects automatically.
        </div>
    </div>
    """, unsafe_allow_html=True)

    jd_text = st.text_area(
        "JOB DESCRIPTION INPUT",
        height=280,
        placeholder="Paste any job description here...\n\nExample:\nWe are looking for a Data Scientist with experience in:\n- Python, PyTorch, TensorFlow\n- NLP and Computer Vision\n- MLOps and deployment\n- LLMs and RAG pipelines",
        label_visibility="collapsed"
    )

    col_analyze, col_clear = st.columns([3, 1])
    with col_analyze:
        analyze_btn = st.button("ANALYZE JOB DESCRIPTION")
    with col_clear:
        if st.button("CLEAR"):
            st.session_state.analysis_done = False
            st.session_state.analysis_data = None
            st.rerun()

    if analyze_btn:
        if not jd_text.strip():
            st.warning("Please paste a job description first.")
        else:
            with st.spinner("Extracting keywords and matching projects..."):
                try:
                    response = requests.post(
                        f"{api_url}/analyze-jd",
                        json={"job_description": jd_text, "output_name": output_name},
                        timeout=120
                    )
                    if response.status_code == 200:
                        data = response.json()
                        st.session_state.analysis_data = data
                        st.session_state.analysis_done = True
                        st.success("Analysis complete!")
                    else:
                        st.error(f"API Error {response.status_code}: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error(f"Cannot connect to API at `{api_url}`. Make sure FastAPI server is running.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # RESULTS
    if st.session_state.analysis_done and st.session_state.analysis_data:
        data = st.session_state.analysis_data
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Analysis Results")

        # Metrics row
        keywords = data.get("keywords", [])
        projects = data.get("selected_projects", [])
        job_title = data.get("job_title", "Not detected")

        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(keywords)}</div>
                <div class="metric-label">Keywords Found</div>
            </div>""", unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">{len(projects)}</div>
                <div class="metric-label">Projects Matched</div>
            </div>""", unsafe_allow_html=True)
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-value">ATS</div>
                <div class="metric-label">Ready</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        col_left, col_right = st.columns(2)

        with col_left:
            st.markdown(f"""
            <div class="glass-card">
                <div style="font-size:0.75rem; color:#64748b; letter-spacing:2px; margin-bottom:0.75rem;">
                    DETECTED ROLE
                </div>
                <div style="font-size:1.1rem; font-weight:600; color:#e2e8f0;">{job_title}</div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class="glass-card">
                <div style="font-size:0.75rem; color:#64748b; letter-spacing:2px; margin-bottom:0.75rem;">
                    EXTRACTED KEYWORDS
                </div>
            """, unsafe_allow_html=True)

            if keywords:
                badges = "".join([f'<span class="keyword-badge">{k}</span>' for k in keywords])
                st.markdown(badges, unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#475569; font-size:0.85rem;">No keywords extracted</div>', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        with col_right:
            st.markdown("""
            <div class="glass-card">
                <div style="font-size:0.75rem; color:#64748b; letter-spacing:2px; margin-bottom:0.75rem;">
                    MATCHED PROJECTS
                </div>
            """, unsafe_allow_html=True)

            if projects:
                for p in projects:
                    score = p.get("score", 100)
                    name = p.get("name", "Unknown")
                    st.markdown(f"""
                    <div class="project-card">
                        <span class="project-score">{score}%</span>
                        <div class="project-name">{name}</div>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.markdown('<div style="color:#475569; font-size:0.85rem;">No projects matched</div>', unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)


# ─── TAB 2: GENERATE RESUME ───
with tab2:
    st.markdown("""
    <div class="glass-card">
        <div style="font-size:0.75rem; color:#64748b; letter-spacing:2px; text-transform:uppercase; margin-bottom:0.5rem;">
            Step 2 — Generate Tailored Resume
        </div>
        <div style="color:#94a3b8; font-size:0.85rem;">
            AI builds a custom ATS-optimized resume PDF based on the job description.
        </div>
    </div>
    """, unsafe_allow_html=True)

    if not st.session_state.analysis_done:
        st.info("Analyze a job description first in the ANALYZE JD tab.")

    jd_for_resume = st.text_area(
        "JOB DESCRIPTION",
        height=220,
        value=jd_text if 'jd_text' in dir() and jd_text else "",
        placeholder="Paste job description here (or go to ANALYZE JD tab first)...",
        label_visibility="collapsed",
        key="jd_resume"
    )

    generate_btn = st.button("GENERATE RESUME PDF")

    if generate_btn:
        if not jd_for_resume.strip():
            st.warning("Please paste a job description.")
        else:
            with st.spinner("Building your tailored resume... This may take 10-30 seconds."):
                try:
                    response = requests.post(
                        f"{api_url}/generate-resume",
                        json={"job_description": jd_for_resume, "output_name": output_name},
                        timeout=60
                    )
                    if response.status_code == 200:
                        st.session_state.pdf_bytes = response.content
                        st.session_state.resume_generated = True
                        st.success("Resume generated successfully!")
                    else:
                        st.error(f"API Error {response.status_code}: {response.text}")
                except requests.exceptions.ConnectionError:
                    st.error(f"Cannot connect to API at `{api_url}`. Start the FastAPI server first.")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    if st.session_state.resume_generated and st.session_state.pdf_bytes:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("""
        <div class="glass-card" style="border-color: rgba(16,185,129,0.3); background: rgba(16,185,129,0.05);">
            <div style="color:#34d399; font-size:0.85rem; font-weight:500;">
                Resume ready! Download your ATS-optimized PDF below.
            </div>
        </div>
        """, unsafe_allow_html=True)

        st.download_button(
            label="DOWNLOAD RESUME PDF",
            data=st.session_state.pdf_bytes,
            file_name=output_name,
            mime="application/pdf",
        )


# ─── TAB 3: ARCHITECTURE ───
with tab3:
    st.markdown("### System Architecture")
    st.code("""
RESUME AI Pipeline:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
INPUT: Job Description Text
    │
    ▼
JD PARSER (/analyze-jd)
    │  → Extract job title
    │  → Extract required keywords
    │  → Score against project library
    ▼
RESUME MATCHER
    │  → Rank projects by relevance score
    │  → Select top N projects
    ▼
RESUME WRITER (/generate-resume)
    │  → Build tailored resume structure
    │  → Inject matched keywords
    │  → ATS-optimize formatting
    ▼
PDF EXPORTER
    │  → Render professional PDF
    │  → Return as binary download
    ▼
OUTPUT: ATS-Optimized Resume PDF
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """, language="text")

    st.markdown("### API Endpoints")
    endpoints = [
        ("GET", "/", "Service info"),
        ("GET", "/health", "Health check"),
        ("POST", "/analyze-jd", "Extract keywords + match projects"),
        ("POST", "/generate-resume", "Generate + download PDF resume"),
    ]
    for method, endpoint, desc in endpoints:
        color = "#667eea" if method == "POST" else "#10b981"
        st.markdown(f"""
        <div class="project-card" style="border-left-color: {color};">
            <span style="background:{color}22; color:{color}; padding:2px 8px;
                  border-radius:6px; font-size:0.75rem; font-weight:600;
                  margin-right:10px;">{method}</span>
            <span style="font-weight:600; color:#e2e8f0;">{endpoint}</span>
            <span style="color:#64748b; font-size:0.85rem; margin-left:10px;">— {desc}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### Quick Start")
    st.code("""
# 1. Start FastAPI backend
uvicorn main:app --reload --port 8000

# 2. Start Streamlit frontend
streamlit run frontend.py

# 3. Open browser
http://localhost:8501
    """, language="bash")
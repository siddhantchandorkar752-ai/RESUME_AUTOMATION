import os
import re
import json
import anthropic
from typing import Dict, List
from jd_parser import extract_jd_data
from resume_matcher import build_resume_strategy

# ─── Constants ────────────────────────────────────────────────────────────────
BASE_NAME    = "SIDDHANT CHANDORKAR"
BASE_ROLE    = "AI / ML Engineer • Data Scientist • LLM & RAG Systems Engineer"
BASE_CONTACT = "siddhantchandorkar752@gmail.com | +91 8093700135 | Mumbai / Pune, Maharashtra"
BASE_LINKS   = [
    ("GitHub",      "https://github.com/siddhantchandorkar752-ai"),
    ("LinkedIn",    "https://www.linkedin.com/in/siddhant-chandorkar-752-ai"),
    ("Hugging Face","https://huggingface.co/siddhantchandorkar")
]

PROJECT_URLS = {
    "FAKEWATCH — Deepfake Forensic Intelligence System":
        "https://huggingface.co/spaces/siddhantchandorkar/fakewatch-deepfake-ai",
    "VERITAS-W — LLM Hallucination Detection & Auto-Correction Engine":
        "https://veritas-2-siddhantchandorkar752-ai.streamlit.app/",
    "SENTINEX — Mental Health Intelligence AI":
        "https://huggingface.co/spaces/siddhantchandorkar/sentinex-mental-health-ai",
    "SENTINEL v2.0 — Real-Time Driver Drowsiness Detection":
        "https://huggingface.co/spaces/siddhantchandorkar/sentinel",
    "PulseML — ML Monitoring & Data Drift Detection Platform":
        "https://pulseml-siddhantchandorkar.streamlit.app/"
}

# ─── Static baseline skills (always present) ─────────────────────────────────
STATIC_SKILLS = {
    "languages": ["Python", "SQL", "JavaScript (basic)", "Bash/Shell"],
    "frameworks_libraries": [
        "PyTorch", "TensorFlow", "Scikit-Learn", "XGBoost",
        "ONNX Runtime", "Weights & Biases", "MLflow"
    ],
    "ml_ai": [
        "LLaMA 3.3 70B", "Groq API", "HuggingFace Transformers",
        "RoBERTa", "DistilBERT", "Prompt Engineering", "PEFT/LoRA",
        "OpenAI-compatible APIs", "LangChain", "LangGraph",
        "RAG Pipelines", "FAISS", "ChromaDB", "Tavily Search API",
        "LLM Orchestration", "Hallucination Detection", "Tool-Use Agents"
    ],
    "computer_vision": [
        "OpenCV", "MediaPipe", "YOLOv8", "EfficientNet-B4",
        "MobileNetV3", "GradCAM", "FaceMesh", "PERCLOS", "EAR/MAR"
    ],
    "cloud_devops": [
        "Docker", "FastAPI", "Uvicorn", "Streamlit", "Gradio",
        "Evidently AI", "Hugging Face Spaces", "CI/CD basics"
    ],
    "databases_tools": [
        "Pandas", "NumPy", "Plotly", "Matplotlib", "Seaborn",
        "SQLite", "PyMuPDF", "EasyOCR", "yfinance"
    ],
    "platforms": [
        "Git", "GitHub", "Google Colab", "Kaggle",
        "VS Code", "Jupyter Notebook", "Linux/Ubuntu"
    ]
}

# ─── Claude client ────────────────────────────────────────────────────────────
_client = None

def _get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            raise EnvironmentError("ANTHROPIC_API_KEY not set.")
        _client = anthropic.Anthropic(api_key=api_key)
    return _client


# ─── 1. Claude-powered summary rewrite ───────────────────────────────────────
BASE_SUMMARY = (
    "AI/ML Engineer and Data Scientist with 7+ production-deployed ML systems spanning Computer Vision, NLP, "
    "Generative AI, LLM Engineering, Agentic AI, and MLOps. Proven ability to architect and independently ship "
    "end-to-end AI pipelines — from raw data ingestion through Docker-containerized deployment on Hugging Face "
    "Spaces and Streamlit Cloud — using Python, PyTorch, TensorFlow, and LangChain. Hands-on expertise in RAG "
    "systems, LLM hallucination detection, real-time inference APIs (FastAPI), and ML monitoring pipelines with "
    "automated data drift alerting (PSI, KS-test). Independently delivered research-grade architectures "
    "(EfficientNet-B4 + Transformer fusion, multi-model NLP ensembles) with live public demos — zero-setup "
    "accessible. Targeting AI Engineer, ML Engineer, and Data Scientist roles where shipping production AI at "
    "speed matters."
)

def build_summary(jd_title: str, jd_keywords: List[str], jd_raw: str = "") -> str:
    """
    Claude rewrites the summary to naturally embed ALL JD keywords
    without changing the candidate's identity or adding false claims.
    """
    try:
        client = _get_client()
        kw_str = ", ".join(jd_keywords[:80])  # cap to avoid token overflow

        prompt = f"""You are an expert ATS resume writer.

TASK: Rewrite the PROFESSIONAL SUMMARY below so it:
1. Naturally embeds as many of these JD keywords as possible: {kw_str}
2. Preserves ALL factual claims — do NOT add technologies or experiences not in the original.
3. Keeps the same professional, confident, first-person tone.
4. Stays under 120 words.
5. Flows as a single paragraph — no bullet points.
6. Does NOT start with "I".

ORIGINAL SUMMARY:
\"\"\"{BASE_SUMMARY}\"\"\"

JOB TITLE TARGET: {jd_title}

Return ONLY the rewritten summary paragraph. No preamble, no quotes."""

        msg = _get_client().messages.create(
            model="claude-opus-4-5",
            max_tokens=512,
            messages=[{"role": "user", "content": prompt}]
        )
        result = msg.content[0].text.strip().strip('"').strip("'")
        return result if len(result) > 80 else BASE_SUMMARY

    except Exception as e:
        print(f"[resume_writer] Summary rewrite failed: {e}. Using base.")
        return _legacy_inject(BASE_SUMMARY, jd_keywords)


def _legacy_inject(summary: str, jd_keywords: list) -> str:
    """Fallback: old hardcoded injection logic."""
    jd = " ".join(x.lower() for x in jd_keywords)
    additions = []
    checks = [
        ("fastapi",     "real-time inference APIs (FastAPI)"),
        ("pytorch",     "PyTorch"),
        ("tensorflow",  "TensorFlow"),
        ("rag",         "RAG systems"),
        ("llm",         "LLM workflows"),
        ("backend",     "backend APIs"),
        ("api",         "backend APIs"),
        ("monitor",     "ML monitoring pipelines"),
        ("deployment",  "Docker-containerized deployment"),
    ]
    for kw, phrase in checks:
        if kw in jd and phrase.lower() not in summary.lower():
            additions.append(phrase)
    for item in additions:
        summary += f" {item},"
    return summary.rstrip(",") + "."


# ─── 2. Dynamic skills section builder ───────────────────────────────────────
def _merge_skills(categorized_from_jd: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Merge JD-extracted categorized keywords into static baseline.
    Deduplicated. JD keywords injected at front of each category for ATS priority.
    """
    merged = {k: list(v) for k, v in STATIC_SKILLS.items()}

    category_map = {
        # jd_parser category → our static key
        "languages":            "languages",
        "frameworks_libraries": "frameworks_libraries",
        "ml_ai":                "ml_ai",
        "cloud_devops":         "cloud_devops",
        "databases_tools":      "databases_tools",
        "methodologies":        "cloud_devops",   # fold into devops
        "domain_terms":         "ml_ai",          # fold into ml_ai
        "soft_skills":          None,              # skip — handled separately
        "all":                  "ml_ai",          # fallback bucket
    }

    for jd_cat, skills in categorized_from_jd.items():
        target = category_map.get(jd_cat)
        if target is None:
            continue
        existing_lower = {s.lower() for s in merged[target]}
        for skill in skills:
            if skill.lower() not in existing_lower:
                merged[target].insert(0, skill)   # JD keywords first → ATS priority
                existing_lower.add(skill.lower())

    return merged


def _render_skills_section(merged: Dict[str, List[str]], jd_keywords: List[str]) -> List[str]:
    """
    Renders TECHNICAL SKILLS section lines.
    Highlights JD-matched keywords (appear first in each line).
    """
    lines = []

    label_map = {
        "languages":            "Languages",
        "frameworks_libraries": "ML / DL Frameworks",
        "ml_ai":                "LLMs, GenAI & RAG",
        "computer_vision":      "Computer Vision",
        "cloud_devops":         "MLOps & Deployment",
        "databases_tools":      "Data Engineering",
        "platforms":            "Tools & Platforms",
    }

    jd_lower = {k.lower() for k in jd_keywords}

    for key, label in label_map.items():
        skills = merged.get(key, [])
        if not skills:
            continue
        # JD-matched skills → bold marker (for PDF renderer) or just first
        matched = [s for s in skills if s.lower() in jd_lower]
        rest    = [s for s in skills if s.lower() not in jd_lower]
        ordered = matched + rest
        lines.append(f"{label}: {', '.join(ordered)}")

    return lines


# ─── 3. Main builder ──────────────────────────────────────────────────────────
def build_tailored_resume(jd_text: str) -> Dict:
    jd       = extract_jd_data(jd_text)
    strategy = build_resume_strategy(jd["keywords"])

    return {
        "job_title":         jd["title"],
        "keywords":          jd["keywords"],
        "categorized":       jd.get("categorized", {}),
        "matched_keywords":  strategy.get("matched_keywords", []),
        "summary":           build_summary(jd["title"], jd["keywords"], jd.get("raw_text", "")),
        "selected_projects": strategy["selected_projects"],
    }


# ─── 4. Renderer ─────────────────────────────────────────────────────────────
def render_resume_text(tailored: Dict) -> str:
    lines = []

    # ── Header ────────────────────────────────────────────────────────────────
    lines.append(BASE_NAME)
    lines.append(BASE_ROLE)
    lines.append(BASE_CONTACT)
    lines.append(" | ".join(f"{k}: {u}" for k, u in BASE_LINKS))
    lines.append("")

    # ── Summary ───────────────────────────────────────────────────────────────
    lines.append("PROFESSIONAL SUMMARY")
    lines.append(tailored["summary"])
    lines.append("")

    # ── Technical Skills (dynamic) ────────────────────────────────────────────
    lines.append("TECHNICAL SKILLS")
    merged = _merge_skills(tailored.get("categorized", {}))
    skill_lines = _render_skills_section(merged, tailored["keywords"])
    lines.extend(skill_lines)
    lines.append("")

    # ── Projects ──────────────────────────────────────────────────────────────
    lines.append("PROJECTS")
    for p in tailored["selected_projects"]:
        url   = PROJECT_URLS.get(p["name"], "")
        title = f"**{p['name']}**"
        if url:
            title += f" | Live Demo: {url}"
        title += f"  {p['years']}"
        lines.append(title)

        # Show project skills + JD-matched keywords highlighted
        proj_skills    = p.get("skills", [])
        matched_extras = [
            kw for kw in p.get("matched_keywords", [])
            if kw not in proj_skills
        ][:4]  # max 4 extras to keep clean
        all_skills = proj_skills + matched_extras
        lines.append(" · ".join(all_skills))

        for b in p.get("bullets", []):
            lines.append(f"• {b}")
        lines.append("")

    # ── Education ─────────────────────────────────────────────────────────────
    lines.append("EDUCATION")
    lines.append("Bachelor of Science (B.Sc) — Statistics, Mathematics & Computer Science  2023 – 2026")
    lines.append("D.G. Tatkare Mahavidyalaya, Mangaon | Raigad, Maharashtra | CGPA: 7.64 / 10")
    lines.append("")

    # ── Certifications ────────────────────────────────────────────────────────
    lines.append("CERTIFICATIONS & TRAINING")
    lines.append("Data Science & Generative AI — PW Skills (Physics Wallah)")
    lines.append("• Completed comprehensive curriculum covering Machine Learning, Deep Learning, Computer Vision, NLP, Generative AI, Agentic AI, RAG architecture, and MLOps.")
    lines.append("• Delivered hands-on projects spanning end-to-end ML pipelines, Transformer architectures, LLM integration with LangChain, and production deployment on cloud platforms.")
    lines.append("Data Analytics Job Simulation — Deloitte (via Forage) | May 2026")
    lines.append("• Completed Deloitte's official job simulation covering data analysis and forensic technology workflows, applying analytical techniques in a real-world enterprise consulting context.")
    lines.append("• Practised industry-standard data investigation and forensic analytics tasks aligned with Deloitte's internal data engineering and analytics practice.")
    lines.append("")

    # ── Key Achievements ──────────────────────────────────────────────────────
    lines.append("KEY ACHIEVEMENTS")
    lines.append("• 7+ production AI apps deployed on Hugging Face Spaces and Streamlit Cloud with live public demos — accessible without local setup or API key configuration.")
    lines.append("• Independently shipped systems across 5 AI domains (Computer Vision, NLP, Generative AI, Agentic AI, MLOps) — covering the full modern AI engineering stack solo.")
    lines.append("• Implemented research-grade architectures (EfficientNet-B4 + Transformer fusion; multi-model NLP ensemble for clinical risk scoring) without team support.")
    lines.append("• Resolved complex production issues: Docker multi-stage builds, Git LFS binary removal, Python version compatibility across 6+ Hugging Face Space environments.")
    lines.append("• Built and shipped a complete MLOps monitoring platform (drift detection, REST API, alerting) — typically a team effort — as a solo project.")

    return "\n".join(lines)

import re
import os
import json
from groq import Groq
from typing import List, Dict, Any, Optional

# =========================
# CONFIG
# =========================

MODEL_NAME  = "llama-3.3-70b-versatile"
MAX_TOKENS  = 8000  # Groq supports large context

FALLBACK_SKILLS = [
    "python", "sql", "fastapi", "streamlit", "gradio", "docker",
    "pytorch", "tensorflow", "scikit-learn", "xgboost", "opencv",
    "mediapipe", "langchain", "langgraph", "llm", "rag", "mlops",
    "hugging face", "transformers", "faiss", "chromadb", "javascript",
    "bash", "linux", "pandas", "numpy", "plotly", "matplotlib",
    "seaborn", "sqlite", "uvicorn", "evidently ai", "mlflow",
    "aws", "gcp", "azure", "postgresql", "mysql", "mongodb", "redis",
    "rest api", "grpc", "github", "git", "jira", "agile", "scrum",
    "kubernetes", "ci/cd", "prometheus", "grafana", "airflow",
    "spark", "kafka", "dbt", "snowflake", "bigquery", "redshift",
    "openai", "gemini", "anthropic", "groq", "mistral", "cohere",
    "langsmith", "weights & biases", "ray", "triton", "onnx",
    "peft", "lora", "qlora", "fine-tuning", "instruction tuning",
    "vector database", "pinecone", "weaviate", "milvus", "qdrant"
]

CANONICAL_MAP = {
    "py torch": "PyTorch", "pytorch": "PyTorch",
    "tf": "TensorFlow", "tensor flow": "TensorFlow",
    "scikit learn": "scikit-learn", "sklearn": "scikit-learn",
    "huggingface": "Hugging Face", "hugging face": "Hugging Face",
    "open ai": "OpenAI", "gpt api": "OpenAI API",
    "azure open ai": "Azure OpenAI",
    "restapi": "REST API", "rest api": "REST API",
    "ci cd": "CI/CD", "ml ops": "MLOps",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "natural language processing": "NLP",
    "computer vision": "Computer Vision",
    "llm": "LLM", "rag": "RAG",
    "faiss": "FAISS", "chromadb": "ChromaDB",
    "postgres": "PostgreSQL", "postgresql": "PostgreSQL",
    "mongo db": "MongoDB", "mongodb": "MongoDB",
    "google cloud platform": "Google Cloud Platform",
    "gcp": "Google Cloud Platform",
    "amazon web services": "AWS", "aws": "AWS",
    "microsoft azure": "Azure", "azure": "Azure",
    "lang chain": "LangChain", "lang graph": "LangGraph",
    "evidently ai": "Evidently AI", "uvicorn": "Uvicorn",
    "plot ly": "Plotly", "mat plot lib": "Matplotlib",
    "weights and biases": "Weights & Biases", "wandb": "Weights & Biases",
    "low rank adaptation": "LoRA", "lora": "LoRA",
    "retrieval augmented generation": "RAG",
    "large language model": "LLM",
    "vector db": "Vector Database",
    "k8s": "Kubernetes",
}

# =========================
# CLIENT
# =========================

_client: Optional[Groq] = None

def _get_client() -> Groq:
    global _client
    if _client is None:
        api_key = None
        try:
            import streamlit as st
            api_key = st.secrets.get("GROQ_API_KEY", None)
        except Exception:
            pass
        if not api_key:
            api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise EnvironmentError("GROQ_API_KEY not set.")
        _client = Groq(api_key=api_key)
    return _client

# =========================
# TEXT UTILITIES
# =========================

def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r"[\n\r\t]+", " ", text)
    text = re.sub(r"[^a-z0-9\+\#\.\-\s\/]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def dedupe_list(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for item in items:
        if not item:
            continue
        x = item.strip()
        key = x.lower()
        if key and key not in seen:
            seen.add(key)
            out.append(x)
    return out

def normalize_term(term: str) -> str:
    if not term:
        return term
    t = term.strip()
    key = clean_text(t)
    if key in CANONICAL_MAP:
        return CANONICAL_MAP[key]
    key2 = key.replace("  ", " ")
    if key2 in CANONICAL_MAP:
        return CANONICAL_MAP[key2]
    return t

def normalize_list(items: List[str]) -> List[str]:
    return dedupe_list([normalize_term(x) for x in items if x and str(x).strip()])

def safe_json_loads(raw: str, default: Any) -> Any:
    try:
        raw = raw.strip()
        raw = re.sub(r"^```(?:json)?", "", raw, flags=re.IGNORECASE).strip()
        raw = re.sub(r"```$", "", raw).strip()
        # Find first { or [ and last } or ]
        start = min(
            (raw.find("{") if raw.find("{") >= 0 else len(raw)),
            (raw.find("[") if raw.find("[") >= 0 else len(raw))
        )
        if start < len(raw):
            raw = raw[start:]
        return json.loads(raw)
    except Exception:
        return default

# =========================
# FALLBACK
# =========================

def extract_keywords_static(jd_text: str) -> List[str]:
    text = clean_text(jd_text)
    found = []
    for skill in FALLBACK_SKILLS:
        if skill in text:
            found.append(normalize_term(skill))
    return dedupe_list(found)

def infer_title_static(text: str) -> str:
    patterns = [
        r"machine learning engineer", r"data scientist", r"ai engineer",
        r"ml engineer", r"software engineer", r"backend engineer",
        r"frontend engineer", r"full.?stack", r"data engineer",
        r"nlp engineer", r"research engineer", r"product manager",
        r"devops engineer", r"platform engineer", r"analyst",
        r"scientist", r"developer", r"specialist", r"associate", r"intern",
    ]
    for p in patterns:
        m = re.search(p, text)
        if m:
            return m.group(0).title()
    return "Unknown"

# =========================
# GROQ CALL
# =========================

def _call_groq(prompt: str, max_tokens: int = MAX_TOKENS) -> str:
    client = _get_client()
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an elite enterprise ATS and talent intelligence engine. "
                    "You return STRICT valid JSON only. No markdown, no commentary, no preamble. "
                    "Start your response directly with { or [."
                )
            },
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.0,
        top_p=1.0,
    )
    return response.choices[0].message.content.strip()

# =========================
# MASTER PROMPT
# =========================

def _build_master_prompt(jd_text: str) -> str:
    return f"""You are an enterprise-grade Job Description Intelligence Engine.

Read the entire JD carefully and return STRICT JSON only.
Do NOT wrap in markdown. Do NOT add commentary. Start with {{

Perform complete hiring-requirement decomposition like a modern ATS combined with a senior recruiter, hiring manager, and talent intelligence platform.

Rules:
- Use ONLY evidence from the JD.
- Do NOT hallucinate or invent skills.
- Normalize skills to canonical names (e.g. "pytorch" → "PyTorch").
- Remove duplicates across all arrays.
- If a field is not present in the JD, use empty string or empty array.
- Return valid JSON only — no trailing commas.

Output schema (fill every field):
{{
  "job_title": "",
  "seniority": "",
  "industry": "",
  "domain": "",
  "department": "",
  "team_function": "",
  "business_context": "",
  "business_problem": "",
  "required_experience": "",
  "education": [],
  "certifications": [],
  "responsibilities": [],
  "technical_skills": [],
  "soft_skills": [],
  "tools": [],
  "frameworks": [],
  "libraries": [],
  "cloud_platforms": [],
  "databases": [],
  "apis": [],
  "programming_languages": [],
  "methodologies": [],
  "concepts": [],
  "business_skills": [],
  "normalized_terms": [
    {{"original_term": "", "canonical_term": ""}}
  ],
  "requirement_classification": {{
    "must_have": [],
    "strongly_preferred": [],
    "good_to_have": [],
    "optional": []
  }},
  "importance_scoring": [
    {{"skill": "", "importance": 0, "reason": ""}}
  ],
  "hiring_signals": [
    {{"signal": "", "importance": "", "evidence": ""}}
  ],
  "responsibility_decomposition": [
    {{"responsibility": "", "action": "", "technology": [], "outcome": "", "business_impact": ""}}
  ],
  "ats_keywords": {{
    "primary_keywords": [],
    "variations": [],
    "synonyms": [],
    "alternate_recruiter_terminology": []
  }},
  "role_archetype": {{
    "official_title": "",
    "actual_role": "",
    "role_archetype": "",
    "explanation": ""
  }},
  "ideal_candidate_profile": {{
    "experience": [],
    "skills": [],
    "projects": [],
    "technologies": [],
    "behaviors": [],
    "leadership_traits": []
  }},
  "resume_matching_object": {{
    "critical_keywords": [],
    "secondary_keywords": [],
    "experience_requirements": [],
    "project_requirements": [],
    "technology_requirements": [],
    "behavioral_requirements": [],
    "business_requirements": []
  }}
}}

JD:
\"\"\"{jd_text}\"\"\"
"""

def _build_fallback_prompt(jd_text: str) -> str:
    return f"""Extract a concise JSON object from the JD below.
Return strict JSON only — start with {{, no markdown.

{{
  "job_title": "",
  "seniority": "",
  "industry": "",
  "domain": "",
  "required_experience": "",
  "education": [],
  "certifications": [],
  "responsibilities": [],
  "technical_skills": [],
  "soft_skills": [],
  "tools": [],
  "frameworks": [],
  "libraries": [],
  "cloud_platforms": [],
  "databases": [],
  "apis": [],
  "programming_languages": [],
  "methodologies": [],
  "concepts": [],
  "business_skills": []
}}

Use only evidence from the JD.

JD:
\"\"\"{jd_text}\"\"\"
"""

# =========================
# MAIN EXTRACTION
# =========================

def _clean_data(data: Dict[str, Any], jd_text: str) -> Dict[str, Any]:
    """Validate + clean the raw extracted dict."""
    list_fields = [
        "education", "certifications", "responsibilities", "technical_skills",
        "soft_skills", "tools", "frameworks", "libraries", "cloud_platforms",
        "databases", "apis", "programming_languages", "methodologies",
        "concepts", "business_skills"
    ]
    str_fields = [
        "job_title", "seniority", "industry", "domain", "department",
        "team_function", "business_context", "business_problem", "required_experience"
    ]

    for k in str_fields:
        data[k] = str(data.get(k, "")).strip()
    for k in list_fields:
        val = data.get(k, [])
        data[k] = normalize_list([str(x) for x in val]) if isinstance(val, list) else []

    # normalized_terms
    if isinstance(data.get("normalized_terms"), list):
        norm = []
        for item in data["normalized_terms"]:
            if isinstance(item, dict):
                orig = str(item.get("original_term", "")).strip()
                canon = str(item.get("canonical_term", "")).strip()
                if orig or canon:
                    norm.append({"original_term": orig, "canonical_term": normalize_term(canon or orig)})
        data["normalized_terms"] = norm
    else:
        data["normalized_terms"] = []

    # requirement_classification
    rc = data.get("requirement_classification", {})
    if not isinstance(rc, dict):
        rc = {}
    for k in ["must_have", "strongly_preferred", "good_to_have", "optional"]:
        rc[k] = normalize_list([str(x) for x in rc.get(k, [])]) if isinstance(rc.get(k), list) else []
    data["requirement_classification"] = rc

    # importance_scoring
    if isinstance(data.get("importance_scoring"), list):
        cleaned = []
        for item in data["importance_scoring"]:
            if not isinstance(item, dict):
                continue
            skill = str(item.get("skill", "")).strip()
            if skill:
                cleaned.append({
                    "skill": normalize_term(skill),
                    "importance": int(item.get("importance", 0) or 0),
                    "reason": str(item.get("reason", "")).strip()
                })
        data["importance_scoring"] = cleaned
    else:
        data["importance_scoring"] = []

    # hiring_signals
    if isinstance(data.get("hiring_signals"), list):
        hs = []
        for item in data["hiring_signals"]:
            if isinstance(item, dict):
                hs.append({
                    "signal": str(item.get("signal", "")).strip(),
                    "importance": str(item.get("importance", "")).strip(),
                    "evidence": str(item.get("evidence", "")).strip()
                })
        data["hiring_signals"] = hs
    else:
        data["hiring_signals"] = []

    # responsibility_decomposition
    if isinstance(data.get("responsibility_decomposition"), list):
        rd = []
        for item in data["responsibility_decomposition"]:
            if isinstance(item, dict):
                tech = item.get("technology", [])
                rd.append({
                    "responsibility": str(item.get("responsibility", "")).strip(),
                    "action": str(item.get("action", "")).strip(),
                    "technology": normalize_list([str(x) for x in tech]) if isinstance(tech, list) else [],
                    "outcome": str(item.get("outcome", "")).strip(),
                    "business_impact": str(item.get("business_impact", "")).strip()
                })
        data["responsibility_decomposition"] = rd
    else:
        data["responsibility_decomposition"] = []

    # ats_keywords
    ak = data.get("ats_keywords", {})
    if not isinstance(ak, dict):
        ak = {}
    for k in ["primary_keywords", "variations", "synonyms", "alternate_recruiter_terminology"]:
        ak[k] = normalize_list([str(x) for x in ak.get(k, [])]) if isinstance(ak.get(k), list) else []
    data["ats_keywords"] = ak

    # role_archetype
    ra = data.get("role_archetype", {})
    if not isinstance(ra, dict):
        ra = {}
    for k in ["official_title", "actual_role", "role_archetype", "explanation"]:
        ra[k] = str(ra.get(k, "")).strip()
    data["role_archetype"] = ra

    # ideal_candidate_profile
    icp = data.get("ideal_candidate_profile", {})
    if not isinstance(icp, dict):
        icp = {}
    for k in ["experience", "skills", "projects", "technologies", "behaviors", "leadership_traits"]:
        icp[k] = normalize_list([str(x) for x in icp.get(k, [])]) if isinstance(icp.get(k), list) else []
    data["ideal_candidate_profile"] = icp

    # resume_matching_object
    rmo = data.get("resume_matching_object", {})
    if not isinstance(rmo, dict):
        rmo = {}
    for k in ["critical_keywords", "secondary_keywords", "experience_requirements",
               "project_requirements", "technology_requirements", "behavioral_requirements", "business_requirements"]:
        rmo[k] = normalize_list([str(x) for x in rmo.get(k, [])]) if isinstance(rmo.get(k), list) else []
    data["resume_matching_object"] = rmo

    if not data["job_title"]:
        data["job_title"] = infer_title_static(clean_text(jd_text))

    return data


def extract_jd_intelligence(jd_text: str) -> Dict[str, Any]:
    try:
        raw = _call_groq(_build_master_prompt(jd_text))
        data = safe_json_loads(raw, default={})
        if not isinstance(data, dict) or not data:
            raise ValueError("Invalid JSON from Groq master prompt")
        data = _clean_data(data, jd_text)
        return data
    except Exception as e:
        print(f"[jd_parser] master extraction failed: {e}")
        return extract_jd_intelligence_fallback(jd_text)


def extract_jd_intelligence_fallback(jd_text: str) -> Dict[str, Any]:
    try:
        raw = _call_groq(_build_fallback_prompt(jd_text), max_tokens=3000)
        data = safe_json_loads(raw, default={})
    except Exception:
        data = {}

    if not isinstance(data, dict):
        data = {}

    text = clean_text(jd_text)
    keywords = extract_keywords_static(jd_text)
    job_title = str(data.get("job_title", "")).strip() or infer_title_static(text)
    required_experience = str(data.get("required_experience", "")).strip()

    def _safe_list(key):
        val = data.get(key, [])
        return normalize_list([str(x) for x in val]) if isinstance(val, list) else []

    return {
        "job_title": job_title,
        "seniority": str(data.get("seniority", "")).strip(),
        "industry": str(data.get("industry", "")).strip(),
        "domain": str(data.get("domain", "")).strip(),
        "department": "", "team_function": "",
        "business_context": "", "business_problem": "",
        "required_experience": required_experience,
        "education": _safe_list("education"),
        "certifications": _safe_list("certifications"),
        "responsibilities": _safe_list("responsibilities"),
        "technical_skills": _safe_list("technical_skills") or keywords,
        "soft_skills": _safe_list("soft_skills"),
        "tools": _safe_list("tools"),
        "frameworks": _safe_list("frameworks"),
        "libraries": _safe_list("libraries"),
        "cloud_platforms": _safe_list("cloud_platforms"),
        "databases": _safe_list("databases"),
        "apis": _safe_list("apis"),
        "programming_languages": _safe_list("programming_languages"),
        "methodologies": _safe_list("methodologies"),
        "concepts": _safe_list("concepts"),
        "business_skills": _safe_list("business_skills"),
        "normalized_terms": [{"original_term": k, "canonical_term": normalize_term(k)} for k in keywords],
        "requirement_classification": {
            "must_have": keywords[:12],
            "strongly_preferred": keywords[12:20],
            "good_to_have": keywords[20:28],
            "optional": keywords[28:]
        },
        "importance_scoring": [
            {"skill": k, "importance": 9 if i < 5 else 7 if i < 12 else 5, "reason": "Detected in JD."}
            for i, k in enumerate(keywords[:25])
        ],
        "hiring_signals": [],
        "responsibility_decomposition": [
            {"responsibility": r, "action": r.split(" ", 1)[0], "technology": [], "outcome": "", "business_impact": ""}
            for r in _safe_list("responsibilities")
        ],
        "ats_keywords": {
            "primary_keywords": keywords,
            "variations": keywords,
            "synonyms": [],
            "alternate_recruiter_terminology": []
        },
        "role_archetype": {
            "official_title": job_title,
            "actual_role": job_title,
            "role_archetype": "General Technical Role",
            "explanation": "Fallback classification."
        },
        "ideal_candidate_profile": {
            "experience": [required_experience] if required_experience else [],
            "skills": keywords,
            "projects": [],
            "technologies": keywords,
            "behaviors": [],
            "leadership_traits": []
        },
        "resume_matching_object": {
            "critical_keywords": keywords[:10],
            "secondary_keywords": keywords[10:20],
            "experience_requirements": [required_experience] if required_experience else [],
            "project_requirements": [],
            "technology_requirements": keywords,
            "behavioral_requirements": [],
            "business_requirements": []
        },
        "raw_text": jd_text
    }

# =========================
# COMPATIBILITY WRAPPERS
# =========================

def extract_keywords(jd_text: str) -> List[str]:
    try:
        data = extract_jd_intelligence(jd_text)
        kws = []
        for k in [
            "technical_skills", "tools", "frameworks", "libraries",
            "cloud_platforms", "databases", "apis", "programming_languages",
            "methodologies", "concepts", "business_skills", "soft_skills", "certifications"
        ]:
            val = data.get(k, [])
            if isinstance(val, list):
                kws.extend(val)
        # Also pull from ats_keywords primary
        ak = data.get("ats_keywords", {})
        kws.extend(ak.get("primary_keywords", []))
        kws.extend(ak.get("variations", []))
        if not kws:
            kws = extract_keywords_static(jd_text)
        return dedupe_list([normalize_term(x) for x in kws if x])
    except Exception:
        return extract_keywords_static(jd_text)


def extract_jd_data(jd_text: str) -> Dict[str, Any]:
    data = extract_jd_intelligence(jd_text)
    return {
        "title": data.get("job_title", "Unknown"),
        "keywords": extract_keywords(jd_text),
        "categorized": {
            "languages": data.get("programming_languages", []),
            "frameworks_libraries": dedupe_list(
                (data.get("frameworks", []) or []) + (data.get("libraries", []) or [])
            ),
            "ml_ai": dedupe_list(
                [x for x in (data.get("concepts", []) or []) if x] +
                [x for x in (data.get("technical_skills", []) or []) if x]
            ),
            "cloud_devops": dedupe_list(
                (data.get("cloud_platforms", []) or []) + (data.get("tools", []) or [])
            ),
            "databases_tools": dedupe_list(
                (data.get("databases", []) or []) + (data.get("apis", []) or [])
            ),
            "methodologies": data.get("methodologies", []),
            "soft_skills": data.get("soft_skills", []),
            "domain_terms": dedupe_list(
                (data.get("concepts", []) or []) +
                ([data.get("industry", "")] if data.get("industry") else []) +
                ([data.get("domain", "")] if data.get("domain") else [])
            ),
        },
        "raw_text": jd_text,
        "full_intelligence": data
    }

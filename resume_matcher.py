from typing import Dict, List, Tuple, Any
import re

# =========================
# ALIAS MAP (expanded)
# =========================

ALIASES: Dict[str, List[str]] = {
    "machine learning": ["ml", "scikit-learn", "xgboost", "lightgbm", "catboost", "random forest", "gradient boosting"],
    "deep learning": ["pytorch", "tensorflow", "keras", "neural network", "cnn", "rnn", "lstm", "gru", "attention"],
    "nlp": ["natural language processing", "transformers", "bert", "roberta", "gpt", "llm", "spacy", "nltk", "text classification", "ner", "sentiment analysis"],
    "llm": ["large language model", "gpt", "llama", "claude", "gemini", "groq", "openai", "mistral", "cohere", "palm", "foundation model"],
    "rag": ["retrieval augmented generation", "langchain", "langgraph", "faiss", "chromadb", "tavily", "pinecone", "weaviate", "vector search", "semantic search"],
    "computer vision": ["cv", "opencv", "mediapipe", "yolo", "efficientnet", "resnet", "vit", "image processing", "object detection", "segmentation"],
    "mlops": ["ml ops", "mlflow", "evidently", "wandb", "model monitoring", "ci/cd", "deployment", "model registry", "experiment tracking", "data drift"],
    "api development": ["rest api", "fastapi", "flask", "django", "endpoint", "microservice", "grpc", "graphql"],
    "docker": ["containerization", "container", "kubernetes", "k8s", "helm", "docker compose"],
    "cloud": ["aws", "gcp", "azure", "hugging face spaces", "cloud deploy", "ec2", "s3", "lambda", "cloud run", "vertex ai"],
    "database": ["sql", "sqlite", "postgresql", "mysql", "mongodb", "redis", "nosql", "vector database"],
    "data science": ["pandas", "numpy", "matplotlib", "seaborn", "plotly", "eda", "analysis", "data cleaning", "feature engineering"],
    "explainability": ["xai", "gradcam", "shap", "lime", "interpretability", "trustworthy ai", "responsible ai"],
    "real-time": ["real time", "low latency", "streaming", "live", "sub-second", "async", "concurrent"],
    "workflow orchestration": ["langgraph", "agentic", "pipeline", "orchestration", "airflow", "prefect", "dagster"],
    "production deployment": ["docker", "fastapi", "streamlit", "gradio", "hugging face spaces", "render", "railway", "heroku", "cloud run"],
    "system design": ["modular architecture", "async", "api backend", "microservice", "distributed systems", "scalable"],
    "data engineering": ["etl", "data pipeline", "ingestion", "spark", "kafka", "dbt", "data warehouse", "data lake"],
    "monitoring": ["evidently ai", "drift detection", "alerting", "logging", "metrics", "prometheus", "grafana", "observability"],
    "security": ["oauth", "jwt", "api key", "token", "auth", "authentication", "authorization", "rbac"],
    "fine-tuning": ["peft", "lora", "qlora", "instruction tuning", "supervised fine-tuning", "sft", "rlhf"],
    "agentic ai": ["tool use", "function calling", "agent", "multi-agent", "autonomous", "tool calling", "react agent"],
    "evaluation": ["benchmarking", "metrics", "accuracy", "f1", "auc", "roc", "precision", "recall", "evaluation framework"],
    "business impact": ["latency reduction", "cost reduction", "accuracy improvement", "automation", "efficiency", "revenue", "roi"],
}

# =========================
# CAPABILITY MAP
# =========================

CAPABILITY_MAP: Dict[str, List[str]] = {
    "Build Agentic AI Solutions": [
        "LLM Integration", "Prompt Engineering", "Tool Calling", "Workflow Orchestration",
        "System Design", "Production Deployment", "Agentic AI"
    ],
    "Integrate Enterprise Systems": [
        "REST APIs", "Authentication", "OAuth", "Data Integration", "Backend Engineering", "API Development"
    ],
    "Create Real-Time AI Applications": [
        "Low Latency", "Streaming", "API Development", "Frontend Integration", "Production Deployment"
    ],
    "Develop Monitoring Platforms": [
        "Observability", "Logging", "Metrics", "Alerting", "Data Drift Detection", "MLOps"
    ],
    "Build Computer Vision Systems": [
        "Image Processing", "Video Processing", "Model Inference", "Explainability", "Deployment", "Computer Vision"
    ],
    "Build NLP Systems": [
        "Text Processing", "Transformer Models", "Classification", "Inference Pipelines", "Evaluation", "NLP"
    ],
    "Build MLOps Platforms": [
        "Model Monitoring", "Data Drift Detection", "Experiment Tracking", "Model Registry", "CI/CD", "MLOps"
    ],
    "Build RAG Systems": [
        "Vector Search", "Retrieval Augmented Generation", "LLM Integration", "Document Processing", "Semantic Search"
    ],
}

# =========================
# UTILITIES
# =========================

def _normalize(text: str) -> str:
    return text.lower().strip()

def _dedupe(items: List[str]) -> List[str]:
    seen = set()
    out = []
    for x in items:
        y = x.strip()
        k = y.lower()
        if y and k not in seen:
            seen.add(k)
            out.append(y)
    return out

def _expand_keywords(keywords: List[str]) -> List[str]:
    expanded = set(_normalize(k) for k in keywords if k)
    for kw in list(expanded):
        for canonical, aliases in ALIASES.items():
            canon_n = _normalize(canonical)
            alias_ns = [_normalize(a) for a in aliases]
            if kw == canon_n or kw in alias_ns:
                expanded.add(canon_n)
                expanded.update(alias_ns)
    return list(expanded)

def _capabilities_from_jd_keywords(jd_keywords: List[str]) -> List[str]:
    expanded = set(_expand_keywords(jd_keywords))
    caps = set()
    for kw in expanded:
        for canonical, aliases in ALIASES.items():
            if kw == _normalize(canonical) or kw in [_normalize(a) for a in aliases]:
                caps.add(canonical)
    return sorted(caps)

# =========================
# PROJECT CAPABILITY ENGINE
# =========================

def _derive_project_capabilities(project: Dict[str, Any]) -> Dict[str, Any]:
    text = " ".join(
        [project.get("name", "")] +
        project.get("skills", []) +
        project.get("bullets", [])
    )
    ntext = _normalize(text)
    capabilities = set()

    for canonical, aliases in ALIASES.items():
        tokens = [_normalize(canonical)] + [_normalize(a) for a in aliases]
        if any(t in ntext for t in tokens):
            capabilities.add(canonical)

    signal_map = [
        (["api", "fastapi", "flask", "endpoint", "rest"], ["Backend Engineering", "API Development"]),
        (["docker", "container", "kubernetes", "deployment", "spaces", "render", "railway"], ["Production Deployment", "Containerization"]),
        (["streamlit", "gradio", "frontend", "dashboard", "ui"], ["Frontend Integration"]),
        (["async", "thread", "daemon", "low latency", "real-time", "sub-second"], ["Low Latency", "System Design"]),
        (["drift", "monitoring", "alert", "metrics", "logging", "psi", "ks-test", "evidently"], ["Observability", "Alerting", "Data Drift Detection", "MLOps"]),
        (["gradcam", "xai", "interpretability", "explainability", "shap"], ["Explainability"]),
        (["langchain", "langgraph", "rag", "tavily", "llama", "groq", "openai", "claude", "gemini"], ["LLM Integration", "Prompt Engineering", "Workflow Orchestration", "RAG"]),
        (["modular architecture", "pipeline", "orchestration", "independent modules", "microservice"], ["System Design", "Modular Architecture"]),
        (["authentication", "oauth", "jwt", "api key", "token"], ["Authentication", "Security"]),
        (["integration", "connect", "external", "web sources"], ["Data Integration"]),
        (["fine-tun", "lora", "qlora", "peft", "instruction"], ["Fine-tuning", "LLM Engineering"]),
        (["transformer", "bert", "roberta", "distil", "attention"], ["Transformer Models", "NLP"]),
        (["efficientnet", "resnet", "yolo", "mediapipe", "opencv", "facemesh"], ["Computer Vision", "Deep Learning"]),
        (["xgboost", "lightgbm", "scikit", "sklearn", "random forest"], ["Machine Learning"]),
        (["pandas", "numpy", "eda", "feature engineering"], ["Data Science"]),
        (["tool use", "function calling", "agent", "agentic", "multi-agent"], ["Agentic AI", "LLM Integration"]),
        (["vector", "faiss", "chromadb", "pinecone", "weaviate", "semantic search"], ["RAG", "Vector Search"]),
        (["evaluation", "benchmark", "f1", "auc", "roc", "accuracy metric"], ["Evaluation"]),
    ]
    for signals, caps in signal_map:
        if any(s in ntext for s in signals):
            capabilities.update(caps)

    return {"capabilities": sorted(capabilities), "evidence_text": ntext}


def _build_jd_requirement_graph(jd_requirements: List[str]) -> Dict[str, List[str]]:
    graph = {}
    for req in jd_requirements:
        req_n = _normalize(req)
        underlying = set()

        pattern_map = [
            (["agentic ai", "agent", "autonomous"], ["LLM Integration", "Prompt Engineering", "Tool Calling", "Workflow Orchestration", "System Design", "Production Deployment", "Agentic AI"]),
            (["enterprise", "integrat"], ["REST APIs", "Authentication", "OAuth", "Data Integration", "Backend Engineering"]),
            (["real-time", "low latency", "streaming"], ["Low Latency", "Streaming", "API Development", "Frontend Integration", "Production Deployment"]),
            (["monitor", "drift", "observ"], ["Observability", "Logging", "Metrics", "Alerting", "Data Drift Detection", "MLOps"]),
            (["vision", "image", "video", "detection"], ["Computer Vision", "Image Processing", "Model Inference", "Explainability", "Deployment"]),
            (["nlp", "text", "language", "sentiment"], ["NLP", "Text Processing", "Transformer Models", "Classification"]),
            (["rag", "retrieval", "vector", "semantic"], ["RAG", "Vector Search", "LLM Integration", "Document Processing"]),
            (["fine-tun", "lora", "peft", "instruction"], ["Fine-tuning", "LLM Engineering", "LLM Integration"]),
            (["mlops", "pipeline", "deploy", "productio"], ["MLOps", "Production Deployment", "CI/CD", "Model Monitoring"]),
            (["data engineer", "etl", "pipeline", "warehouse"], ["Data Engineering", "ETL", "Data Pipeline"]),
        ]
        for signals, caps in pattern_map:
            if any(s in req_n for s in signals):
                underlying.update(caps)

        if not underlying:
            underlying.update(CAPABILITY_MAP.get(req, []))

        graph[req] = sorted(underlying)
    return graph


# =========================
# SCORING ENGINE
# =========================

def _score_project_against_jd(
    project: Dict[str, Any],
    jd_caps: List[str],
    jd_requirements: List[str],
    jd_keywords: List[str]
) -> Dict[str, Any]:
    proj = _derive_project_capabilities(project)
    proj_caps = set(proj["capabilities"])
    proj_text = proj["evidence_text"]

    jd_graph = _build_jd_requirement_graph(jd_requirements)
    jd_underlying = set()
    for caps in jd_graph.values():
        jd_underlying.update(caps)

    # 1. Capability match (40%)
    capability_overlap = proj_caps.intersection(jd_underlying)
    capability_match = min(100.0, (len(capability_overlap) / max(len(jd_underlying), 1)) * 100.0)

    # 2. Responsibility match (20%) — action verbs
    responsibility_keywords = [
        "built", "designed", "implemented", "deployed", "engineered",
        "architected", "integrated", "automated", "developed", "created",
        "resolved", "optimized", "reduced", "improved", "shipped"
    ]
    responsibility_hits = sum(1 for kw in responsibility_keywords if kw in proj_text)
    responsibility_match = min(100.0, responsibility_hits * 7.0)

    # 3. Technical keyword match (20%)
    technical_keywords = set(_expand_keywords(jd_keywords))
    tech_hits = sum(1 for kw in technical_keywords if len(kw) > 3 and kw in proj_text)
    technical_match = min(100.0, tech_hits * 6.0)

    # 4. Production signals (10%)
    production_signals = [
        "deployed", "docker", "api", "fastapi", "streamlit", "gradio",
        "hugging face spaces", "render", "railway", "real-time", "latency",
        "monitoring", "alerting", "sub-second", "cpu", "gpu", "inference"
    ]
    prod_hits = sum(1 for kw in production_signals if kw in proj_text)
    production_score = min(100.0, prod_hits * 9.0)

    # 5. Business impact signals (10%)
    business_signals = [
        "fraud", "risk", "detection", "automation", "latency", "efficiency",
        "faster", "accuracy", "scorecard", "monitoring", "alerting",
        "decision", "reduction", "improved", "zero-setup", "roc-auc"
    ]
    bus_hits = sum(1 for kw in business_signals if kw in proj_text)
    business_score = min(100.0, bus_hits * 9.0)

    overall = (
        capability_match    * 0.40 +
        responsibility_match * 0.20 +
        technical_match     * 0.20 +
        production_score    * 0.10 +
        business_score      * 0.10
    )

    return {
        "name":                        project.get("name", ""),
        "years":                       project.get("years", ""),
        "skills":                      project.get("skills", []),
        "bullets":                     project.get("bullets", []),
        "problem_solved":              _infer_problem_solved(project),
        "business_use_case":           _infer_business_use_case(project),
        "skills_demonstrated":         sorted(proj_caps),
        "matched_keywords":            sorted(capability_overlap),
        "engineering_capabilities":    _extract_engineering_capabilities(proj_text),
        "deployment_capabilities":     _extract_deployment_capabilities(proj_text),
        "system_design_capabilities":  _extract_system_design_capabilities(proj_text),
        "production_readiness_signals":_extract_production_signals(proj_text),
        "overall_match_score":         round(overall, 2),
        "capability_match_score":      round(capability_match, 2),
        "responsibility_match_score":  round(responsibility_match, 2),
        "technical_match_score":       round(technical_match, 2),
        "production_score":            round(production_score, 2),
        "business_score":              round(business_score, 2),
        "reasoning":                   _build_reasoning(project, capability_overlap, jd_underlying)
    }


def _rank_bullets_for_project(
    project: Dict[str, Any],
    jd_keywords: List[str],
    jd_requirements: List[str]
) -> List[Dict[str, Any]]:
    req_graph = _build_jd_requirement_graph(jd_requirements)
    req_caps = set()
    for caps in req_graph.values():
        req_caps.update(caps)

    expanded_jd = set(_expand_keywords(jd_keywords))

    scored = []
    for bullet in project.get("bullets", []):
        b = _normalize(bullet)
        capability_hits  = sum(1 for c in req_caps if _normalize(c) in b)
        technical_hits   = sum(1 for kw in expanded_jd if len(kw) > 3 and kw in b)
        production_hits  = sum(1 for x in ["deployed", "docker", "api", "fastapi", "streamlit", "real-time", "monitoring"] if x in b)
        action_hits      = sum(1 for x in ["built", "designed", "implemented", "engineered", "architected", "resolved", "optimized"] if x in b)
        score = capability_hits * 4 + technical_hits * 3 + production_hits * 2 + action_hits * 1
        scored.append({
            "bullet": bullet,
            "score":  score,
            "why":    "High JD capability match" if capability_hits else "Supporting technical evidence"
        })
    scored.sort(key=lambda x: -x["score"])
    return scored


# =========================
# HELPERS
# =========================

def _infer_problem_solved(project: Dict[str, Any]) -> str:
    name = _normalize(project.get("name", ""))
    if "deepfake" in name:       return "Detect manipulated visual media and explain forgery evidence."
    if "hallucination" in name or "veritas" in name: return "Verify and correct LLM claims using grounded sources."
    if "mental health" in name or "sentinex" in name: return "Detect risk signals from text conversations."
    if "drowsiness" in name or "sentinel" in name:   return "Detect driver fatigue in real time and trigger alerts."
    if "drift" in name or "pulseml" in name:         return "Monitor ML model health and data drift in production."
    return "Solve a domain-specific AI/software engineering problem."

def _infer_business_use_case(project: Dict[str, Any]) -> str:
    name = _normalize(project.get("name", ""))
    if "deepfake" in name:       return "Forensic verification and media trust."
    if "hallucination" in name or "veritas" in name: return "LLM quality assurance and answer reliability."
    if "mental health" in name or "sentinex" in name: return "Safety monitoring and mental health risk triage."
    if "drowsiness" in name or "sentinel" in name:   return "Road safety and fatigue prevention."
    if "drift" in name or "pulseml" in name:         return "Model monitoring and production ML governance."
    return "Business automation and intelligent decision support."

def _extract_engineering_capabilities(text: str) -> List[str]:
    caps = set()
    if any(x in text for x in ["architected", "modular", "pipeline", "system"]): caps.add("System Design")
    if any(x in text for x in ["implemented", "engineered", "built"]):           caps.add("Implementation")
    if any(x in text for x in ["integrated", "api", "endpoint"]):                caps.add("API Development")
    if any(x in text for x in ["automated", "daemon", "async"]):                 caps.add("Automation")
    if any(x in text for x in ["optimized", "reduced", "improved"]):             caps.add("Performance Optimization")
    return sorted(caps)

def _extract_deployment_capabilities(text: str) -> List[str]:
    caps = set()
    if any(x in text for x in ["deployed", "docker", "hugging face spaces", "streamlit", "gradio"]): caps.add("Production Deployment")
    if "docker" in text:                  caps.add("Containerization")
    if "api" in text or "fastapi" in text: caps.add("Backend Deployment")
    if "kubernetes" in text or "k8s" in text: caps.add("Orchestration")
    return sorted(caps)

def _extract_system_design_capabilities(text: str) -> List[str]:
    caps = set()
    if any(x in text for x in ["modular", "pipeline", "orchestration", "multi-model"]): caps.add("Modular Architecture")
    if any(x in text for x in ["real-time", "low latency", "async", "thread"]):          caps.add("Low Latency Design")
    if any(x in text for x in ["monitoring", "alert", "drift"]):                         caps.add("Observability Design")
    if any(x in text for x in ["microservice", "distributed", "scalable"]):              caps.add("Distributed Systems")
    return sorted(caps)

def _extract_production_signals(text: str) -> List[str]:
    checks = [
        ("docker", "Containerized"), ("deployed", "Deployed"),
        ("fastapi", "API-backed"), ("streamlit", "Interactive UI"),
        ("gradio", "Interactive UI"), ("hugging face spaces", "Hosted in production"),
        ("real-time", "Real-time"), ("latency", "Latency-sensitive"),
        ("monitoring", "Monitoring"), ("alert", "Alerting"),
        ("sub-second", "Sub-second inference"), ("cpu", "CPU-optimized"),
    ]
    signals = []
    seen = set()
    for needle, label in checks:
        if needle in text and label not in seen:
            signals.append(label)
            seen.add(label)
    return signals

def _build_reasoning(project: Dict[str, Any], overlap: set, jd_underlying: set) -> str:
    if not jd_underlying:
        return "No JD capability graph provided."
    pct = round(len(overlap) / max(len(jd_underlying), 1) * 100, 1)
    if overlap:
        return f"Matches {len(overlap)}/{len(jd_underlying)} JD capabilities ({pct}%). Strong production evidence."
    return "Limited capability overlap with this JD."

def _project_coverage_analysis(
    jd_requirements: List[str],
    top_projects: List[Dict[str, Any]]
) -> Dict[str, List[str]]:
    jd_graph = _build_jd_requirement_graph(jd_requirements)
    covered = set()
    for p in top_projects:
        covered.update(p.get("skills_demonstrated", []))

    fully_covered, partially_covered, missing = [], [], []
    for req, caps in jd_graph.items():
        overlap = covered.intersection(set(caps))
        if len(overlap) == len(set(caps)) and caps: fully_covered.append(req)
        elif overlap:                               partially_covered.append(req)
        else:                                       missing.append(req)

    return {"fully_covered": fully_covered, "partially_covered": partially_covered, "missing": missing}

# =========================
# MAIN API
# =========================

def build_resume_strategy(
    jd_keywords: List[str],
    jd_requirements: List[str] = None
) -> Dict[str, Any]:
    if jd_requirements is None:
        jd_requirements = jd_keywords

    all_projects = _get_all_projects()
    jd_caps = _capabilities_from_jd_keywords(jd_keywords)

    scored_projects = []
    for proj in all_projects:
        scored = _score_project_against_jd(proj, jd_caps, jd_requirements, jd_keywords)
        bullet_ranking = _rank_bullets_for_project(proj, jd_keywords, jd_requirements)
        scored["bullet_ranking"] = bullet_ranking
        top_bullets = sorted(bullet_ranking, key=lambda x: -x["score"])[:4]
        scored["bullets"] = [b["bullet"] for b in top_bullets]
        scored_projects.append(scored)

    scored_projects.sort(key=lambda p: -p["overall_match_score"])

    top_projects = scored_projects[:5]

    all_matched = []
    seen = set()
    for p in top_projects:
        for kw in p.get("matched_keywords", []):
            if kw.lower() not in seen:
                seen.add(kw.lower())
                all_matched.append(kw)

    return {
        "selected_projects":          top_projects,
        "matched_keywords":           all_matched,
        "total_projects_evaluated":   len(all_projects),
        "jd_requirement_graph":       _build_jd_requirement_graph(jd_requirements),
        "project_coverage_analysis":  _project_coverage_analysis(jd_requirements, top_projects),
        "top_3_projects":             top_projects[:3],
        "top_5_projects":             top_projects[:5],
        "top_7_projects":             scored_projects[:7],
    }

# =========================
# PROJECT BANK
# =========================

def _get_all_projects() -> List[Dict]:
    return [
        {
            "name": "FAKEWATCH — Deepfake Forensic Intelligence System",
            "years": "2024 – 2025",
            "skills": ["EfficientNet-B4", "Transformer", "GradCAM", "PyTorch", "Gradio", "Docker", "FastAPI"],
            "bullets": [
                "Architected a dual-stream deepfake detection pipeline fusing EfficientNet-B4 spatial features with an 8-head Transformer encoder for temporal modeling, enabling frame-level forgery localization on image and video inputs.",
                "Engineered a GradCAM explainability layer generating pixel-level heatmaps over manipulated facial regions, making model decisions interpretable for downstream forensic review.",
                "Resolved a critical production blocker via LayerNorm fusion to eliminate BatchNorm instability at batch-size-1 inference — unblocking live Hugging Face deployment.",
                "Containerized with Docker and deployed to Hugging Face Spaces; delivers sub-second inference with real-time confidence scoring — zero-setup accessible."
            ]
        },
        {
            "name": "VERITAS-W — LLM Hallucination Detection & Auto-Correction Engine",
            "years": "2024 – 2025",
            "skills": ["LLaMA 3.3 70B", "Groq", "Tavily RAG", "LangChain", "Streamlit", "LLM Orchestration", "RAG"],
            "bullets": [
                "Designed a 5-stage hallucination detection pipeline: claim extraction → real-time web search (Tavily RAG) → verdict scoring (TRUE / FALSE / UNCERTAIN) → auto-correction → structured scorecard generation.",
                "Grounded every extracted claim against live web sources via Tavily + LLaMA 3.3 70B (Groq API), achieving <3-second end-to-end verification latency per document.",
                "Automated false-claim rewriting with sourced corrections, outputting a per-claim confidence scorecard — directly reducing LLM output error rates in production.",
                "Built with a modular architecture isolating claim extraction, search, scoring, and correction into independent, testable modules for maintainability."
            ]
        },
        {
            "name": "SENTINEX — Mental Health Intelligence AI",
            "years": "2024 – 2025",
            "skills": ["RoBERTa", "DistilRoBERTa", "HuggingFace Transformers", "Gradio", "Docker", "PyTorch", "NLP"],
            "bullets": [
                "Built a multi-model NLP fusion system combining three Transformer models (emotion detection, sentiment analysis, sarcasm detection) to move beyond single-signal text classification.",
                "Engineered a 4-tier risk escalation engine (LOW → CRITICAL) with a 10-message rolling window — detecting risk escalation patterns across conversation turns, not isolated messages.",
                "Implemented a rule-based clinical marker scanner covering 6 signal categories (hopelessness, isolation, dissociation) with threshold-calibrated scoring aligned to published mental health guidelines.",
                "Deployed on Hugging Face Spaces with Docker; includes integrated crisis helpline resources and responsible-AI safety disclaimers."
            ]
        },
        {
            "name": "SENTINEL v2.0 — Real-Time Driver Drowsiness Detection",
            "years": "2024",
            "skills": ["MediaPipe", "OpenCV", "FastAPI", "SQLite", "Gradio", "ONNX Runtime", "Computer Vision"],
            "bullets": [
                "Built a low-latency fatigue detection pipeline using MediaPipe 468-point FaceMesh computing EAR, MAR, PERCLOS, and head pose (solvePnP) at ~60 ms/frame on CPU — no GPU required.",
                "Implemented NHTSA-standard PERCLOS over a 60-second rolling window with Kalman filtering on the EAR signal, measurably reducing false positive rate vs. baseline threshold approach.",
                "Designed an async 1000 Hz alarm daemon thread for non-blocking audio alerts; state machine handles ALERT / WARNING / MICROSLEEP transitions without frame drops.",
                "Deployed with Gradio UI + FastAPI REST backend + SQLite session logging; full stack runs on Hugging Face Spaces CPU tier."
            ]
        },
        {
            "name": "PulseML — ML Monitoring & Data Drift Detection Platform",
            "years": "2024",
            "skills": ["XGBoost", "Evidently AI", "FastAPI", "Streamlit", "Plotly", "Docker", "MLOps"],
            "bullets": [
                "Built an end-to-end MLOps monitoring platform on the IEEE-CIS fraud detection dataset (590K transactions, 3.5% fraud rate); trained XGBoost classifier to ROC-AUC 0.9212.",
                "Implemented PSI and KS-test drift detection via Evidently AI with automated alerting when feature drift share exceeds threshold or F1 score degrades >5%.",
                "Designed a 7-endpoint FastAPI REST API for programmatic monitoring access; Streamlit dashboard with Plotly visualizations tracks model KPIs in real time.",
                "Containerized full stack with Docker using modular architecture cleanly separating data loading, model training, drift monitoring, alerting, and API layers."
            ]
        }
    ]
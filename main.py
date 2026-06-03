from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from typing import Optional
from jd_parser import extract_jd_data
from resume_matcher import build_resume_strategy
from resume_writer import build_tailored_resume, render_resume_text
from pdf_exporter import export_pdf
import os

app = FastAPI(title="Resume Automation API", version="1.0.0")

class JDRequest(BaseModel):
    job_description: str
    output_name: Optional[str] = "tailored_resume.pdf"

@app.get("/")
def root():
    return {"message": "Resume Automation API is running"}

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/analyze-jd")
def analyze_jd(payload: JDRequest):
    if not payload.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")

    jd_data = extract_jd_data(payload.job_description)
    strategy = build_resume_strategy(jd_data["keywords"])

    return {
        "job_title": jd_data["title"],
        "keywords": jd_data["keywords"],
        "selected_projects": [
            {"name": p["name"], "score": p.get("score", 100)}
            for p in strategy["selected_projects"]
        ]
    }

@app.post("/generate-resume")
def generate_resume(payload: JDRequest):
    if not payload.job_description.strip():
        raise HTTPException(status_code=400, detail="Job description cannot be empty")

    tailored = build_tailored_resume(payload.job_description)
    resume_text = render_resume_text(tailored)

    os.makedirs("output", exist_ok=True)
    pdf_path = export_pdf(resume_text, f"output/{payload.output_name}")

    with open(pdf_path, "rb") as f:
        pdf_bytes = f.read()

    headers = {
        "Content-Disposition": f'attachment; filename="{payload.output_name}"'
    }

    return Response(content=pdf_bytes, media_type="application/pdf", headers=headers)
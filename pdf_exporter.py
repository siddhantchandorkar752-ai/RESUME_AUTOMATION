import os
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable

def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def _fmt_line(line: str) -> str:
    text = _escape(line.strip())

    if text.startswith("**") and "**" in text[2:]:
        end = text.find("**", 2)
        title = text[2:end]
        rest = text[end + 2:]
        return f"<b>{title}</b>{rest}"

    if text.startswith("• "):
        return f"<bullet>&bull;</bullet>{text[2:]}"

    if "Live Demo:" in text and "http" in text:
        parts = text.split("| Live Demo:")
        if len(parts) == 2:
            left = parts[0].strip()
            right = parts[1].strip()
            return f"{left} | <link href='{right}' color='blue'><u>Live Demo</u></link>"

    return text

def export_pdf(text: str, output_path: str = "output/tailored_resume.pdf") -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=24,
        bottomMargin=24
    )

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(
        name="Header",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=18,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#111111"),
        spaceAfter=4
    ))
    styles.add(ParagraphStyle(
        name="SubHeader",
        parent=styles["Normal"],
        fontName="Helvetica-Bold",
        fontSize=9.5,
        leading=11,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#333333"),
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name="Contact",
        parent=styles["Normal"],
        fontSize=8.7,
        leading=10,
        alignment=TA_CENTER,
        textColor=colors.HexColor("#444444"),
        spaceAfter=2
    ))
    styles.add(ParagraphStyle(
        name="Section",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=10.2,
        leading=12,
        textColor=colors.HexColor("#111111"),
        spaceBefore=5,
        spaceAfter=3
    ))
    styles.add(ParagraphStyle(
        name="Body",
        parent=styles["Normal"],
        fontSize=8.7,
        leading=10.3,
        spaceAfter=1.5
    ))
    styles.add(ParagraphStyle(
        name="BulletBody",
        parent=styles["Normal"],
        fontSize=8.6,
        leading=10.2,
        leftIndent=12,
        firstLineIndent=0,
        spaceAfter=1.2
    ))

    lines = text.split("\n")
    story = []

    section_titles = {
        "PROFESSIONAL SUMMARY",
        "TECHNICAL SKILLS",
        "PROJECTS",
        "EDUCATION",
        "CERTIFICATIONS & TRAINING",
        "KEY ACHIEVEMENTS"
    }

    for i, line in enumerate(lines):
        clean = _fmt_line(line)

        if i == 0:
            story.append(Paragraph(clean, styles["Header"]))
        elif i == 1:
            story.append(Paragraph(clean, styles["SubHeader"]))
        elif i in [2, 3]:
            story.append(Paragraph(clean, styles["Contact"]))
        elif clean.strip() == "":
            story.append(Spacer(1, 3))
        elif clean.strip().replace("<b>", "").replace("</b>", "") in section_titles:
            story.append(Spacer(1, 2))
            story.append(HRFlowable(width="100%", thickness=0.45, color=colors.HexColor("#C9C9C9")))
            story.append(Spacer(1, 2))
            story.append(Paragraph(clean, styles["Section"]))
        elif clean.startswith("<bullet>"):
            story.append(Paragraph(clean, styles["BulletBody"], bulletText="•"))
        else:
            story.append(Paragraph(clean, styles["Body"]))

    doc.build(story)
    return output_path
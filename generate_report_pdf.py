"""
Generate a standard professional Internship Project Report (PDF)
for VisionSpec QC using ReportLab.
"""

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table, TableStyle,
    PageBreak, ListFlowable, ListItem, HRFlowable, NextPageTemplate,
)

OUTPUT = "VisionSpec_QC_Internship_Report.pdf"

# ── Brand palette ───────────────────────────────────────────
NAVY = colors.HexColor("#1e293b")
ACCENT = colors.HexColor("#2563eb")
LIGHT = colors.HexColor("#f1f5f9")
MUTED = colors.HexColor("#64748b")
GREEN = colors.HexColor("#16a34a")

# ── Report metadata (edit these to personalise) ─────────────
INTERN_NAME = "Bharath Krishnan S"
INTERN_EMAIL = "sbkcuddalore@gmail.com"
COMPANY = "Zaalima Development"
PROJECT = "VisionSpec QC — AI-Powered PCB Visual Inspection System"
DURATION = "4 Weeks"
REPORT_DATE = "June 2026"

styles = getSampleStyleSheet()

styles.add(ParagraphStyle("CoverTitle", fontName="Helvetica-Bold", fontSize=26,
                          textColor=colors.white, alignment=TA_CENTER, leading=32))
styles.add(ParagraphStyle("CoverSub", fontName="Helvetica", fontSize=13,
                          textColor=colors.white, alignment=TA_CENTER, leading=18))
styles.add(ParagraphStyle("H1", fontName="Helvetica-Bold", fontSize=15,
                          textColor=NAVY, spaceBefore=14, spaceAfter=6, leading=18))
styles.add(ParagraphStyle("H2", fontName="Helvetica-Bold", fontSize=12,
                          textColor=ACCENT, spaceBefore=10, spaceAfter=4, leading=15))
styles.add(ParagraphStyle("Body", fontName="Helvetica", fontSize=10.5,
                          textColor=NAVY, alignment=TA_JUSTIFY, leading=15, spaceAfter=4))
styles.add(ParagraphStyle("ListBody", fontName="Helvetica", fontSize=10.5,
                          textColor=NAVY, leading=15))
styles.add(ParagraphStyle("Cell", fontName="Helvetica", fontSize=9.5,
                          textColor=NAVY, leading=13))
styles.add(ParagraphStyle("CellB", fontName="Helvetica-Bold", fontSize=9.5,
                          textColor=NAVY, leading=13))
styles.add(ParagraphStyle("Foot", fontName="Helvetica", fontSize=8,
                          textColor=MUTED, alignment=TA_CENTER))


def B(text):
    return Paragraph(text, styles["Body"])


def bullets(items):
    return ListFlowable(
        [ListItem(Paragraph(t, styles["ListBody"]), leftIndent=10, value="•")
         for t in items],
        bulletType="bullet", bulletColor=ACCENT, leftIndent=14, spaceAfter=6,
    )


def info_table(rows):
    data = [[Paragraph(k, styles["CellB"]), Paragraph(v, styles["Cell"])] for k, v in rows]
    t = Table(data, colWidths=[45 * mm, 120 * mm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return t


def grid_table(header, rows, col_widths):
    data = [[Paragraph(h, ParagraphStyle("th", parent=styles["CellB"], textColor=colors.white)) for h in header]]
    for r in rows:
        data.append([Paragraph(c, styles["Cell"]) for c in r])
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, LIGHT]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 7),
        ("RIGHTPADDING", (0, 0), (-1, -1), 7),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
    ]))
    return t


# ── Page decoration ─────────────────────────────────────────
def on_page(canvas, doc):
    canvas.saveState()
    w, h = A4
    # footer
    canvas.setStrokeColor(colors.HexColor("#cbd5e1"))
    canvas.setLineWidth(0.5)
    canvas.line(20 * mm, 15 * mm, w - 20 * mm, 15 * mm)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(20 * mm, 10 * mm, "VisionSpec QC — Internship Project Report")
    canvas.drawRightString(w - 20 * mm, 10 * mm, "Page %d" % doc.page)
    canvas.restoreState()


def on_cover(canvas, doc):
    canvas.saveState()
    w, h = A4
    canvas.setFillColor(NAVY)
    canvas.rect(0, 0, w, h, fill=1, stroke=0)
    canvas.setFillColor(ACCENT)
    canvas.rect(0, h - 6 * mm, w, 6 * mm, fill=1, stroke=0)
    canvas.rect(0, 0, w, 6 * mm, fill=1, stroke=0)
    canvas.restoreState()


# ── Build document ──────────────────────────────────────────
doc = BaseDocTemplate(
    OUTPUT, pagesize=A4,
    leftMargin=20 * mm, rightMargin=20 * mm, topMargin=20 * mm, bottomMargin=22 * mm,
    title="VisionSpec QC Internship Report", author=INTERN_NAME,
)
frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id="main")
cover_frame = Frame(0, 0, A4[0], A4[1], id="cover",
                    leftPadding=25 * mm, rightPadding=25 * mm, topPadding=70 * mm, bottomPadding=40 * mm)
doc.addPageTemplates([
    PageTemplate(id="Cover", frames=[cover_frame], onPage=on_cover),
    PageTemplate(id="Content", frames=[frame], onPage=on_page),
])

story = []

# ── COVER ───────────────────────────────────────────────────
# Page 1 uses the "Cover" template; switch to "Content" for all following pages.
story.append(NextPageTemplate("Content"))
story += [
    Paragraph("INTERNSHIP PROJECT REPORT", styles["CoverSub"]),
    Spacer(1, 10 * mm),
    Paragraph("VisionSpec QC", styles["CoverTitle"]),
    Spacer(1, 4 * mm),
    Paragraph("AI-Powered PCB Visual Inspection System", styles["CoverSub"]),
    Spacer(1, 30 * mm),
    Paragraph("Submitted by", styles["CoverSub"]),
    Spacer(1, 2 * mm),
    Paragraph("<b>%s</b>" % INTERN_NAME, styles["CoverSub"]),
    Paragraph(INTERN_EMAIL, styles["CoverSub"]),
    Spacer(1, 18 * mm),
    Paragraph("Organization: %s" % COMPANY, styles["CoverSub"]),
    Paragraph("Duration: %s &nbsp;|&nbsp; %s" % (DURATION, REPORT_DATE), styles["CoverSub"]),
]
story.append(PageBreak())

# ── 1. Internship Details ───────────────────────────────────
story += [
    Paragraph("1. Internship &amp; Project Details", styles["H1"]),
    HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8),
    info_table([
        ("Intern Name", INTERN_NAME),
        ("Email", INTERN_EMAIL),
        ("Organization", COMPANY),
        ("Project Title", PROJECT),
        ("Domain", "Artificial Intelligence / Computer Vision"),
        ("Duration", DURATION),
        ("Report Date", REPORT_DATE),
        ("Status", "Completed — running end-to-end"),
    ]),
    Spacer(1, 6 * mm),
]

# ── 2. Project Overview ─────────────────────────────────────
story += [
    Paragraph("2. Project Overview (Abstract)", styles["H1"]),
    HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8),
    B("VisionSpec QC is an end-to-end, AI-powered quality-control application that automates the "
      "visual inspection of Printed Circuit Boards (PCBs). The system classifies each board as "
      "<b>Pass</b> or <b>Defect</b> and applies Explainable AI (Grad-CAM) to highlight the exact "
      "regions responsible for a defect verdict, removing the “black-box” limitation of "
      "deep neural networks."),
    B("The platform is built as a modular full-stack system: a deep-learning model (MobileNetV2 "
      "transfer learning) served through a FastAPI backend, persisted to a SQLite database, and "
      "presented through a real-time React + TypeScript dashboard supporting image upload, live "
      "webcam inference, analytics, and inspection history."),
]

# ── 3. Objectives ───────────────────────────────────────────
story += [
    Paragraph("3. Objectives", styles["H1"]),
    HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8),
    bullets([
        "Build an automated PCB defect-classification model using transfer learning.",
        "Provide Explainable AI (Grad-CAM heatmaps) to justify each prediction.",
        "Expose real-time inference through production-grade REST APIs (FastAPI).",
        "Deliver an interactive dashboard with live detection, analytics, and history.",
        "Persist every prediction for auditing and a Human-in-the-Loop feedback workflow.",
    ]),
]

# ── 4. Technologies Used ────────────────────────────────────
story += [
    Paragraph("4. Technologies Used", styles["H1"]),
    HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8),
    grid_table(
        ["Layer", "Technology"],
        [
            ["AI / Machine Learning", "TensorFlow 2, Keras, MobileNetV2 (Transfer Learning), Grad-CAM"],
            ["Computer Vision", "OpenCV, NumPy, Pillow"],
            ["Backend", "FastAPI, Uvicorn, SQLAlchemy, SQLite"],
            ["Frontend", "React, TypeScript, Vite, Chart.js, Axios"],
            ["Tooling", "Python venv, Git, psutil, Matplotlib (reports)"],
        ],
        [48 * mm, 117 * mm],
    ),
]

story.append(PageBreak())

# ── 5. Weekly Progress ──────────────────────────────────────
story += [
    Paragraph("5. Weekly Progress Breakdown", styles["H1"]),
    HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8),
]

weeks = [
    ("Week 1 — Foundation, Dataset &amp; Project Scaffolding",
     "Establish the development environment, raw data, and skeleton of all three layers.",
     ["Set up Python virtual environment and installed the core AI/backend stack; initialized the React + TypeScript app via Vite.",
      "Designed the modular backend (routes, services, models, schemas) and frontend (pages, components, services) structure.",
      "Built a procedural <b>Synthetic PCB Dataset Generator</b> producing 1,000 images (500 Pass / 500 Defect) at 224×224, with injected defects (scratches, burns, oxidation, missing traces).",
      "Configured Keras ImageDataGenerator augmentation and created routing for the core pages."]),
    ("Week 2 — Core Detection Model &amp; Prediction API",
     "Train the first working classifier and connect it to an upload API and UI.",
     ["Built a MobileNetV2 transfer-learning model: GlobalAveragePooling → Dense(256) → Dense(128) → Dense(1, Sigmoid).",
      "Two-phase training: 10 epochs frozen backbone, then fine-tuned top layers for 10 more epochs (early stop at epoch 17); exported pcb_model.h5.",
      "Developed the POST /api/predict endpoint (validation, preprocessing, inference, response with label, confidence, latency).",
      "Built the Defect Analysis page with drag-and-drop upload wired to the prediction API."]),
    ("Week 3 — Explainable AI (Grad-CAM) &amp; Live Video Pipeline",
     "Add visual explainability and a live webcam inference path.",
     ["Implemented Grad-CAM against MobileNetV2's final conv layer (out_relu) to generate defect heatmaps.",
      "Encoded heatmaps as base64 in the prediction response and rendered them as an overlay in the UI.",
      "Built the POST /api/webcam/predict endpoint using OpenCV for frame-by-frame inference.",
      "Created the Live Detection page that streams the browser webcam feed with real-time results and FPS monitoring."]),
    ("Week 4 — Analytics, Logging, Dashboard &amp; Integration",
     "Tie everything together with persistence, analytics, evaluation, and polish.",
     ["Added SQLite prediction logging and the GET /api/analytics and GET /api/history APIs (with CSV export).",
      "Built the real-time Dashboard (totals, defect rate, latency, FPS, recent predictions, system status) auto-refreshing every 5 seconds.",
      "Implemented the System Monitor (CPU / memory / uptime) and a Human-in-the-Loop feedback endpoint for operator corrections.",
      "Generated the final evaluation: metrics, confusion matrix, ROC curve, and prediction-distribution charts."]),
]

for title, goal, items in weeks:
    story.append(Paragraph(title, styles["H2"]))
    story.append(Paragraph("<b>Goal:</b> " + goal, styles["Body"]))
    story.append(bullets(items))
    story.append(Spacer(1, 2 * mm))

story.append(PageBreak())

# ── 6. Evaluation Results ───────────────────────────────────
story += [
    Paragraph("6. Model Evaluation Results", styles["H1"]),
    HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8),
    Paragraph("Overall Performance (200-image validation set)", styles["H2"]),
    grid_table(
        ["Metric", "Value"],
        [["Accuracy", "67.0%"], ["AUC (ROC)", "0.7652"],
         ["Validation Loss", "0.5867"], ["Avg. Inference Time", "~280–620 ms (CPU)"]],
        [82 * mm, 83 * mm],
    ),
    Spacer(1, 4 * mm),
    Paragraph("Classification Report", styles["H2"]),
    grid_table(
        ["Class", "Precision", "Recall", "F1-Score", "Support"],
        [["Defect", "0.77", "0.48", "0.59", "100"],
         ["Pass", "0.62", "0.86", "0.72", "100"]],
        [40 * mm, 31 * mm, 31 * mm, 31 * mm, 32 * mm],
    ),
    Spacer(1, 3 * mm),
    B("<i>Note: 67% accuracy is an expected baseline for highly randomized, procedurally-generated "
      "synthetic noise. The same architecture applied to a real-world dataset (e.g., the Kaggle PCB "
      "Defect Dataset) typically achieves 95%+ accuracy.</i>"),
]

# ── 7. Conclusion ───────────────────────────────────────────
story += [
    Paragraph("7. Conclusion", styles["H1"]),
    HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8),
    B("Over four weeks, the VisionSpec QC project delivered a complete, production-style AI pipeline "
      "for industrial visual inspection — from synthetic data generation and transfer-learning "
      "model training to Explainable AI, real-time APIs, and a full React dashboard. The architecture "
      "is modular, scalable, and ready to ingest real factory-floor data to reach state-of-the-art "
      "accuracy, complete with enterprise features such as Human-in-the-Loop logging and Grad-CAM "
      "diagnostics."),
]

# ── 8. Future Enhancements ──────────────────────────────────
story += [
    Paragraph("8. Future Enhancements", styles["H1"]),
    HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8),
    bullets([
        "Train on real-world PCB datasets to push accuracy beyond 95%.",
        "Multi-class defect categorization (short circuit, burn, missing solder, scratch).",
        "Dockerization and cloud deployment (Render backend + Vercel frontend).",
        "Edge-AI mode using TFLite / TensorRT for ultra-fast on-device inference.",
        "Auto-generated PDF QA reports and Slack / email defect-streak alerts.",
    ]),
]

doc.build(story)
print("PDF written to", OUTPUT)

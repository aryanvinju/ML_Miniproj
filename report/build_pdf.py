"""Produce the two-page submission PDF from validated project findings."""

from pathlib import Path
import json

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
METRICS = json.loads((ROOT / "models" / "metrics.json").read_text())
DEST = ROOT / "report" / "writeup.pdf"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCustom", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=16.4, leading=19.5, textColor=colors.HexColor("#102a43"), spaceAfter=11))
styles.add(ParagraphStyle(name="SectionCustom", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10.8, leading=13, textColor=colors.HexColor("#007d80"), spaceBefore=12, spaceAfter=5))
styles.add(ParagraphStyle(name="BodyCustom", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.25, leading=13.1, spaceAfter=7))
styles.add(ParagraphStyle(name="SmallCustom", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.1, leading=11.2, spaceAfter=4))
styles.add(ParagraphStyle(name="SubtitleCustom", parent=styles["BodyText"], fontSize=9.5, leading=13, textColor=colors.HexColor("#557086"), spaceAfter=14))

def p(text, style="BodyCustom"):
    return Paragraph(text, styles[style])

def section(title, text):
    return [p(title, "SectionCustom"), p(text)]

story = [
    p("Predicting a Decline in Patient-Reported Physical Health During Chemotherapy", "TitleCustom"),
    p("Machine learning mini project  |  Educational reproduction  |  8 October 2026", "SubtitleCustom"),
]
story += section("Research question", "Can baseline information identify patients whose PROMIS Global Physical Health (GPH) T-score falls by at least 10 points during chemotherapy? The source study used 1,252 records from Stanford's restricted STARR warehouse and reported a best AUROC of 0.7713 for the decline outcome [1]. This project reproduces the question and a basic modeling workflow, not the source cohort.")
story += section("Data and outcome", "STARR records were unavailable, so a fixed-seed generator created 1,252 <b>fictional</b> patient rows. Pre-treatment inputs were age, baseline GPH and GMH, comorbidity count, prior emergency visits and admissions, hemoglobin, albumin, BMI, cancer stage, and treatment goal. The target is 1 when <font face='Courier'>on_treatment_gph - baseline_gph &lt;= -10</font>. Later GPH is used only to create the label. Selected baseline values have 7% simulated missingness. The generator's relationships are teaching assumptions, not clinical evidence.")
story += section("Methods", "An 80/20 stratified split produced 1,001 training and 251 held-out test rows. Median imputation and standardization of numeric fields, plus one-hot encoding of categories, were fitted inside scikit-learn pipelines. Five-fold cross-validation on the training split compared regularized logistic regression with random forest using mean AUROC. The selected model was refit on the training split and assessed once on the held-out test set. A prior-probability classifier supplied a baseline.")
story.append(p("Model selection and test results", "SectionCustom"))
t = Table([
    ["Measure", "Logistic regression", "Random forest", "Prior baseline"],
    ["Mean CV AUROC", "0.6833", "0.6596", "-"],
    ["Held-out AUROC", "0.7514", "not tested*", "0.5000"],
    ["Held-out Brier score", "0.1916", "not tested*", "0.2277"],
], colWidths=[1.35*inch, 1.45*inch, 1.3*inch, 1.18*inch])
t.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#102a43")),
    ("TEXTCOLOR",(0,0),(-1,0),colors.white),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),
    ("FONTNAME",(0,1),(-1,-1),"Helvetica"),
    ("FONTSIZE",(0,0),(-1,-1),8.2),
    ("BOTTOMPADDING",(0,0),(-1,-1),7),
    ("TOPPADDING",(0,0),(-1,-1),7),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f2f7f8")]),
    ("LINEBELOW",(0,-1),(-1,-1),.5,colors.HexColor("#d9e4eb")),
]))
story.extend([t, Spacer(1,5), p("*Only the model chosen by cross-validation was evaluated on the held-out test set.", "SmallCustom")])
story.append(PageBreak())
story.append(p("Results, interpretation, and limitations", "TitleCustom"))
story += section("Held-out synthetic results", "Logistic regression was selected. In the 251-row test set, AUROC was 0.7514, average precision 0.5962, and Brier score 0.1916. At a prespecified 0.5 threshold, sensitivity was 0.3750 and specificity 0.8834. There were 33 true positives, 55 false negatives, 19 false positives, and 144 true negatives. Synthetic outcome prevalence was 0.3506. These figures describe only the simulation.")
story += section("What the demo shows", "The local web panel accepts pre-treatment values, uses exported logistic-regression coefficients in the browser, and displays an illustrative probability. A presenter can change one input at a time to show how the output responds. No information is sent to a server. The model is a teaching aid and must not be used for clinical decisions.")
story += section("Limitations and next steps", "The original study used hundreds of EHR features; this reproduction uses eleven selected inputs and a simulated label mechanism. It neither reconstructs the STARR cohort nor validates performance in real patients. A real-data project would need authorized de-identified longitudinal records, a defined prediction time and follow-up period, temporal patient-level validation, missing-survey analysis, calibration, subgroup assessment, and review by clinicians and patients. The 0.5 threshold here is illustrative; no clinical action threshold has been established.")
story += section("Reproducibility", "The repository contains a fixed-seed generator, training code, tests, model export, and the web demo. The train/test split, preprocessing, model selection, and metrics can be regenerated with the commands in README. No patient records are included.")
story.append(p("References", "SectionCustom"))
story.append(p("[1] N. Ostberg and D. Peterson. <i>Predicting a Decline in Patient Reported Outcomes for Cancer Patients on Chemotherapy.</i> Stanford CS229, 2020. https://cs229.stanford.edu/proj2020spr/report/Ostberg_Peterson.pdf", "SmallCustom"))
story.append(p("[2] HealthMeasures. <i>PROMIS measures.</i> https://www.promishealth.org/healthmeasures/", "SmallCustom"))

def footer(canvas, doc):
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#557086"))
    canvas.drawString(43, 31, "Educational synthetic-data reproduction | Not for clinical use")
    canvas.drawRightString(570, 31, f"{doc.page} / 2")

doc = SimpleDocTemplate(str(DEST), pagesize=(612,792), leftMargin=43, rightMargin=43, topMargin=43, bottomMargin=50)
doc.build(story, onFirstPage=footer, onLaterPages=footer)
print(DEST)

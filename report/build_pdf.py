"""Build the two-page real-data project write-up."""

from pathlib import Path
import json

from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

ROOT = Path(__file__).resolve().parents[1]
M = json.loads((ROOT / "models" / "real_metrics.json").read_text())
DEST = ROOT / "report" / "writeup.pdf"

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="TitleCustom", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=17, leading=20, textColor=colors.HexColor("#102a43"), spaceAfter=11))
styles.add(ParagraphStyle(name="SectionCustom", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=10.8, leading=13, textColor=colors.HexColor("#007d80"), spaceBefore=12, spaceAfter=5))
styles.add(ParagraphStyle(name="BodyCustom", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.25, leading=13.1, spaceAfter=7))
styles.add(ParagraphStyle(name="SmallCustom", parent=styles["BodyText"], fontName="Helvetica", fontSize=8, leading=11, spaceAfter=4))
styles.add(ParagraphStyle(name="SubtitleCustom", parent=styles["BodyText"], fontSize=9.5, leading=13, textColor=colors.HexColor("#557086"), spaceAfter=14))

def p(text, style="BodyCustom"):
    return Paragraph(text, styles[style])

def section(title, text):
    return [p(title, "SectionCustom"), p(text)]

story = [p("Predicting Quality-of-Life Decline After Adjuvant Chemotherapy", "TitleCustom"),
         p("Real public-data adaptation  |  Machine learning mini project  |  8 October 2026", "SubtitleCustom")]
story += section("Research question", "Can scores measured before chemotherapy predict a fall of at least 10 points in EORTC QLQ-C30 global health status upon completion of adjuvant chemotherapy? This is a real-data adaptation of the Stanford CS229 topic [4]. It changes the questionnaire and assessment time because the original STARR records are unavailable.")
story += section("Data and target", "We used the CC0 dataset from Carmona-Bayonas et al. [1, 2], a prospective breast cancer cohort. Its source workbook has 339 rows; 217 contain both baseline and end-of-treatment global health scores. The binary outcome is <font face='Courier'>HE_end - HE_baseline &lt;= -10</font> on the EORTC 0-100 scale. Predictors are baseline global health, physical, role, emotional, cognitive, and social functioning; baseline fatigue, nausea/vomiting, and pain; and surgery type. No end-of-treatment score enters the predictors.")
story += section("Methods", "A stratified 80/20 split (seed 229) placed 173 patients in training and 44 in a held-out test set. Median imputation, numeric standardization, and one-hot encoding were fit inside each pipeline and cross-validation fold. Five-fold training cross-validation compared regularized logistic regression and random forest by mean AUROC. The selected model was refit on all training rows and tested once. A prior-probability classifier supplied a baseline. The AUROC interval is a descriptive bootstrap over 2,000 held-out resamples.")
story.append(p("Model selection and held-out results", "SectionCustom"))
t = Table([
    ["Measure", "Logistic", "Random forest", "Prior baseline"],
    ["Mean CV AUROC", "0.7884", "0.7696", "-"],
    ["Held-out AUROC", "0.7422", "not tested*", "0.5000"],
    ["Held-out Brier", "0.1914", "not tested*", "0.2314"],
], colWidths=[1.4*inch, 1.2*inch, 1.33*inch, 1.35*inch])
t.setStyle(TableStyle([
    ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#102a43")),("TEXTCOLOR",(0,0),(-1,0),colors.white),
    ("FONTNAME",(0,0),(-1,0),"Helvetica-Bold"),("FONTSIZE",(0,0),(-1,-1),8.3),
    ("BOTTOMPADDING",(0,0),(-1,-1),7),("TOPPADDING",(0,0),(-1,-1),7),
    ("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#f2f7f8")]),
    ("LINEBELOW",(0,-1),(-1,-1),.5,colors.HexColor("#d9e4eb")),
]))
story.extend([t, Spacer(1,5), p("*Only the model chosen by training cross-validation was evaluated on the held-out set.", "SmallCustom")])
story.append(PageBreak())
story.append(p("Results, interpretation, and limitations", "TitleCustom"))
story += section("Held-out performance", "The decline outcome occurred in 78 of 217 paired records (35.94%). Logistic regression was selected. In the 44-person test set, AUROC was 0.7422 (bootstrap 95% interval 0.5738-0.8802), average precision 0.6359, and Brier score 0.1914. At a 0.5 threshold, sensitivity was 0.4375 and specificity 0.8571: 7 true positives, 9 false negatives, 4 false positives, and 24 true negatives. The wide interval reflects the small test set.")
story += section("What the demo shows", "The local web page accepts a hypothetical pre-chemotherapy profile and computes a logistic-regression output in the browser. It makes the trained model inspectable and lets a presenter change one baseline score at a time. Inputs are not transmitted. The displayed probability is exploratory, not a validated risk estimate for an individual patient.")
story += section("Limitations", "This model predicts health status at treatment completion, whereas the Stanford study predicted PROMIS GPH during chemotherapy. It cannot be compared directly with that study's AUROC. All patients came from one source study; only those with paired questionnaires were included, and missing follow-up may bias results. The 10-point target and 0.5 decision threshold are project choices, not patient-level action rules. EORTC advises care in translating group-level score differences to individuals [3]. External validation, calibration, missing-data analysis, and clinical review are needed before any care use.")
story += section("Reproducibility", "The repository includes a checksum-verified download command for the CC0 workbook, provenance, fixed-seed training script, generated metrics, tests, and the local browser demo. It does not redistribute patient-level rows. Training uses only baseline columns and surgery type; all end-of-treatment fields are excluded from predictors.")
story.append(p("References", "SectionCustom"))
story.append(p("[1] Carmona-Bayonas A et al. <i>Prediction of quality of life in early breast cancer upon completion of adjuvant chemotherapy.</i> npj Breast Cancer 7, 92 (2021). doi:10.1038/s41523-021-00296-8", "SmallCustom"))
story.append(p("[2] Carmona-Bayonas A et al. Figshare dataset (2021). doi:10.6084/m9.figshare.14681274", "SmallCustom"))
story.append(p("[3] EORTC Quality of Life. <i>How do I interpret QOL scores?</i> https://qol.eortc.org/faq/how-do-i-interpret-qol-scores/how-do-i-interpret-qol-scores/", "SmallCustom"))
story.append(p("[4] Ostberg N, Peterson D. Stanford CS229 final report (2020). https://cs229.stanford.edu/proj2020spr/report/Ostberg_Peterson.pdf", "SmallCustom"))

def footer(canvas, doc):
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#557086"))
    canvas.drawString(43, 31, "Real public-data research demonstration | Not for clinical use")
    canvas.drawRightString(570, 31, f"{doc.page} / 2")

SimpleDocTemplate(str(DEST), pagesize=(612,792), leftMargin=43, rightMargin=43,
                  topMargin=43, bottomMargin=50).build(story,onFirstPage=footer,onLaterPages=footer)
print(DEST)

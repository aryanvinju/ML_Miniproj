# Predicting a decline in patient-reported health after chemotherapy

An exploratory machine-learning mini project on **real, public, de-identified research data**. It predicts whether a patient's EORTC QLQ-C30 global health status score decreases by at least 10 points between the pre-chemotherapy questionnaire and completion of adjuvant chemotherapy. The cohort comes from [Carmona-Bayonas et al. (2021)](https://doi.org/10.1038/s41523-021-00296-8); the [underlying data](https://doi.org/10.6084/m9.figshare.14681274) are CC0-licensed on Figshare.

This is a real-data **adaptation** of [Ostberg and Peterson's Stanford CS229 project](https://cs229.stanford.edu/proj2020spr/report/Ostberg_Peterson.pdf). Stanford's STARR records are not public. This project uses **EORTC QLQ-C30**, not PROMIS GPH, and predicts the score at **treatment completion**, not during treatment. The original synthetic demonstration is preserved at the [`synthetic-v1` tag](https://github.com/aryanvinju/ML_Miniproj/tree/synthetic-v1).

## Project files

- `data/README.md` — workbook provenance and checksum; `src/download_data.py` downloads it from Figshare
- `src/train_real.py` — cohort filtering, target creation, model selection, evaluation, and browser model export
- `docs/` — interactive local demo that performs inference in the browser
- `report/writeup.pdf` — two-page write-up
- `slides/presentation_real_v2.pptx` — editable seven-slide presentation
- `tests/` — checks for cohort count, outcome definition, and leakage control

## Run the demo

On Windows, double-click `run_demo.bat`, or run this command from the repository root:

```bash
python -m http.server 8000 --directory docs
```

Open [http://localhost:8000](http://localhost:8000). Keep the terminal open while presenting. The browser uses the precomputed `docs/model.json`; no Python packages or server-side prediction endpoint are needed to show the demo. Inputs stay in your browser.

## Reproduce training

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m src.download_data
python -m src.train_real
python -m pytest -q
```

The download command fetches the published CC0 workbook from Figshare and verifies its MD5 checksum. The patient-level workbook stays local and is excluded from Git. Training writes `models/real_metrics.json`, `models/real_model.joblib`, and `docs/model.json`.

## Study definition and methods

The public workbook has 339 rows. We retain 217 with both `HE_baseline` and `HE_end` observed. The target is `HE_end - HE_baseline <= -10` on the EORTC 0–100 global health scale. The model uses only pre-chemotherapy questionnaire domains and surgery type: baseline global health, physical, role, emotional, cognitive, and social functioning; baseline fatigue, nausea/vomiting, and pain; and surgery. No `_end` field is included in predictors.

The 217 paired records are split 80/20 by stratified random sampling (seed 229): 173 for training and 44 for testing. Median imputation, scaling, and categorical encoding are fitted within pipelines and cross-validation folds. Five-fold cross-validation selects between regularized logistic regression and random forest by AUROC. The selected model is evaluated once on the held-out set against a prior-probability baseline.

| Measure | Result |
|---|---:|
| Selected model | Logistic regression |
| Mean training CV AUROC | 0.7884 |
| Held-out AUROC | 0.7422 |
| Bootstrap 95% interval for held-out AUROC | 0.5738–0.8802 |
| Held-out average precision | 0.6359 |
| Held-out Brier score | 0.1914 |
| Held-out sensitivity / specificity at 0.5 | 0.4375 / 0.8571 |

These metrics are exploratory: the test set contains only 44 people, all patients came from the same source study, and the original study found 219 with an end-of-treatment score but only 217 with both scores needed for this decline target. Missing follow-up questionnaires could bias results. The 10-point threshold is a project definition, not a patient-specific clinical action rule. [EORTC warns](https://qol.eortc.org/faq/how-do-i-interpret-the-score-of-a-patient/how-do-i-interpret-the-score-of-a-patient/) that group-level thresholds may not translate directly to individual interpretation.

## References

1. Carmona-Bayonas A et al. *Prediction of quality of life in early breast cancer upon completion of adjuvant chemotherapy*. npj Breast Cancer 7, 92 (2021). https://doi.org/10.1038/s41523-021-00296-8
2. Carmona-Bayonas A et al. Public dataset. Figshare (2021). https://doi.org/10.6084/m9.figshare.14681274
3. Ostberg N, Peterson D. *Predicting a Decline in Patient Reported Outcomes for Cancer Patients on Chemotherapy*. Stanford CS229 (2020). https://cs229.stanford.edu/proj2020spr/report/Ostberg_Peterson.pdf

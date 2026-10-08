# Predicting decline in patient-reported physical health during chemotherapy

An educational machine-learning mini project inspired by [Ostberg and Peterson (2020)](https://cs229.stanford.edu/proj2020spr/report/Ostberg_Peterson.pdf). It predicts whether a patient's PROMIS Global Physical Health (GPH) score will fall by **at least 10 T-score points** during chemotherapy, using only baseline information.

> **Data provenance:** The paper's 1,252 patient records came from the Stanford Research Repository (STARR), a restricted clinical data warehouse. Those records are **not in this repository**. The included generator creates **synthetic, fictional records** for software demonstration. Its scores do not validate a medical prediction model. Never use this demo to make clinical decisions.

## Deliverables

- `src/`: synthetic data generation, leakage-safe training, and export of a small browser model
- `docs/`: interactive, browser-only demo (GitHub Pages compatible)
- `report/`: source text and two-page PDF write-up
- `slides/`: editable PowerPoint presentation
- `tests/`: tests of the outcome definition and training workflow

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python -m src.generate_data --output data/synthetic_patients.csv
python -m src.train --data data/synthetic_patients.csv --output models
python -m http.server 8000 --directory docs
```

Open `http://localhost:8000`. The demo works without a backend; input stays in the browser. Training writes metrics to `models/metrics.json` and a browser-readable model to `docs/model.json`.

On Windows, you can also double-click `run_demo.bat` to launch the already-trained demo. Keep its terminal window open during the presentation.

## Intended study design

The paper defined two targets: GPH decline of at least 10 points and on-treatment GPH at or below 40. This reproduction implements the **decline target** only: `on_treatment_gph - baseline_gph <= -10`. It compares regularized logistic regression and random forest against a prior-probability baseline. The split is stratified by patient, fixed before preprocessing; imputation and scaling are fit in cross-validation folds only. Model selection uses five-fold cross-validation on the training set. A held-out test set is evaluated once. We report AUROC, average precision, Brier score, sensitivity, and specificity at a prespecified 0.5 threshold.

`src/train.py` can also read a real CSV with the documented columns, but this requires an authorized, de-identified dataset and a separate scientific validation plan. No real patient data should be committed to GitHub.

## Input schema

Each row is one fictional or appropriately de-identified patient. Features are all known **before** chemotherapy begins:

| Column | Meaning |
|---|---|
| `age` | Years |
| `baseline_gph` | PROMIS GPH T-score |
| `baseline_gmh` | PROMIS global mental health T-score |
| `comorbidity_count` | Number of prior diagnoses |
| `ed_visits_6m` | Emergency visits in prior six months |
| `hospitalizations_6m` | Admissions in prior six months |
| `hemoglobin_g_dl` | Most recent pre-treatment hemoglobin |
| `albumin_g_dl` | Most recent pre-treatment albumin |
| `bmi` | Body mass index |
| `cancer_stage` | `I`, `II`, `III`, or `IV` |
| `treatment_goal` | `curative` or `palliative` |
| `on_treatment_gph` | Later PROMIS GPH score; **target creation only** |

## Limitations

The source study used much richer EHR features and restricted patient data. This reproduction's selected inputs and synthetic generation mechanism are teaching choices, not a reconstruction of those records. The demo's displayed probability is a model output on fictional data, not an individual risk estimate suitable for care. Distribution shift, missing PROMIS surveys, and treatment timing require attention in any future real-data study.

## References

1. Ostberg N, Peterson D. *Predicting a Decline in Patient Reported Outcomes for Cancer Patients on Chemotherapy*. Stanford CS229, 2020. https://cs229.stanford.edu/proj2020spr/report/Ostberg_Peterson.pdf
2. HealthMeasures. *PROMIS measures*. https://www.promishealth.org/healthmeasures/

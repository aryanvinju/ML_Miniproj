# Predicting Quality-of-Life Decline After Adjuvant Chemotherapy

**Real public data adaptation of the Stanford CS229 patient-reported-outcomes topic**

## Research question

Can scores measured before chemotherapy predict a fall of at least 10 points in EORTC QLQ-C30 global health status upon completion of adjuvant chemotherapy? This changes the Stanford paper's PROMIS GPH/during-treatment endpoint because its STARR records are unavailable. It is a related research question, not a replication.

## Data and outcome

We used the CC0 dataset of Carmona-Bayonas et al. (2021), a prospective breast cancer cohort. The source workbook contains 339 rows; 217 have both baseline and end-of-treatment global health scores and can be labeled. The outcome is `HE_end - HE_baseline <= -10` on the EORTC 0–100 scale. Predictors are baseline global health, physical, role, emotional, cognitive, and social functioning, baseline fatigue, nausea/vomiting, pain, and surgery type. All end-of-treatment fields are excluded. EORTC notes that a 5–10 point difference can be useful for interpreting group changes, but individual-level meaning and scale-specific thresholds require more care.

## Methods

We used a stratified 80/20 split (seed 229): 173 training and 44 held-out patients. Median imputation, standardization, and one-hot encoding are fitted inside each training fold. Five-fold cross-validation compared regularized logistic regression and random forest using AUROC. The better model was refit on the training set and evaluated once on the held-out set. A prior-probability classifier provided a baseline. A 2,000-resample bootstrap of the held-out set yielded a descriptive AUROC interval.

## Results

The decline outcome occurred in 78 of 217 paired records (35.94%). Mean CV AUROC was 0.7884 for logistic regression and 0.7696 for random forest, selecting logistic regression. On 44 held-out patients, AUROC was 0.7422 (bootstrap 95% interval 0.5738–0.8802), average precision 0.6359, and Brier score 0.1914. At threshold 0.5, sensitivity was 0.4375 and specificity 0.8571: 7 true positives, 9 false negatives, 4 false positives, and 24 true negatives. The prior-probability baseline had AUROC 0.5000 and Brier score 0.2314.

## Interpretation and limitations

This result shows that the public cohort supports a working, leakage-aware prediction exercise, but it does not establish a clinically deployable model. The test set is small and all records come from one study. Only patients with both questionnaires are included, so missing follow-up may bias the cohort. The 10-point target and 0.5 classification threshold were chosen for the project, not validated as patient-level action rules. The demo accepts hypothetical baseline profiles and performs local browser inference. The repository provides a checksum-verified download command for the public workbook rather than redistributing patient-level rows. External validation, calibration, missing-data analysis, and clinical review would be needed before any use in care.

## References

1. Carmona-Bayonas A et al. *Prediction of quality of life in early breast cancer upon completion of adjuvant chemotherapy*. npj Breast Cancer 7, 92 (2021). https://doi.org/10.1038/s41523-021-00296-8
2. Carmona-Bayonas A et al. Public dataset. Figshare (2021). https://doi.org/10.6084/m9.figshare.14681274
3. EORTC Quality of Life. *How do I interpret QOL scores?* https://qol.eortc.org/faq/how-do-i-interpret-qol-scores/how-do-i-interpret-qol-scores/
4. Ostberg N, Peterson D. *Predicting a Decline in Patient Reported Outcomes for Cancer Patients on Chemotherapy*. Stanford CS229 (2020). https://cs229.stanford.edu/proj2020spr/report/Ostberg_Peterson.pdf

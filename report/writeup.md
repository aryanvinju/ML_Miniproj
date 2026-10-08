# Predicting a Decline in Patient-Reported Physical Health During Chemotherapy

**Educational reproduction inspired by Ostberg and Peterson (2020)**

## Research question

Can information available before chemotherapy identify patients whose PROMIS Global Physical Health (GPH) T-score falls by at least 10 points during treatment? A 10-point drop corresponds to one population standard deviation on the PROMIS T-score scale. The source paper used 1,252 patients from Stanford's restricted STARR warehouse and reported a best AUROC of 0.7713 for the decline outcome. This mini project reproduces the question and a basic modeling workflow, not the source cohort.

## Data and target

Because STARR records are unavailable, we generate 1,252 **fictional** patient rows with a fixed random seed. Inputs include baseline PROMIS scores, age, stage, treatment goal, prior utilization, comorbidity count, BMI, hemoglobin, and albumin. The binary target equals 1 when `on_treatment_gph - baseline_gph <= -10`. Later GPH is used only to create the target, never as an input. The generator deliberately introduces 7% missingness in selected pre-treatment features. Its outcome mechanism is illustrative and makes no claim about real clinical relationships.

## Methods

We stratified patients into 1,001 training and 251 held-out test rows (80/20, random seed 229). Numeric features are median-imputed and standardized; categorical features are one-hot encoded. All preprocessing is inside each scikit-learn pipeline, so five-fold cross-validation sees only its training fold. We compared regularized logistic regression and a random forest by mean cross-validation AUROC. A constant prior-probability classifier provides a baseline. The selected model was refit on the full training split and evaluated once on the held-out test set. The browser demo exports an auditable logistic regression model.

## Results on fictional data

Mean cross-validation AUROC was 0.6833 for logistic regression and 0.6596 for random forest. Logistic regression was selected. On the 251-row held-out synthetic test set, it reached AUROC 0.7514, average precision 0.5962, and Brier score 0.1916. At a 0.5 decision threshold, sensitivity was 0.3750 and specificity 0.8834 (33 true positives, 55 false negatives, 19 false positives, 144 true negatives). The prior-probability baseline had AUROC 0.5000 and Brier score 0.2277. The synthetic target prevalence was 0.3506.

## Interpretation and limits

The exercise shows a reproducible, leakage-aware workflow and an interactive local demo. It does **not** replicate or validate the Stanford paper: the feature set is smaller, no STARR records were used, and the synthetic labels follow a chosen simulation mechanism. Model metrics on fictional records cannot estimate performance in a hospital. Real-world development would require authorized, de-identified longitudinal data, a defined prediction time and follow-up window, patient-level temporal validation, calibration and subgroup evaluation, and clinical review. The app is for education only and must not guide care.

## References

1. Ostberg N, Peterson D. *Predicting a Decline in Patient Reported Outcomes for Cancer Patients on Chemotherapy*. Stanford CS229, 2020. https://cs229.stanford.edu/proj2020spr/report/Ostberg_Peterson.pdf
2. HealthMeasures. *PROMIS measures*. https://www.promishealth.org/healthmeasures/

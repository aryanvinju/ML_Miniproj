"""Shared feature and outcome definitions."""

NUMERIC = [
    "age", "baseline_gph", "baseline_gmh", "comorbidity_count",
    "ed_visits_6m", "hospitalizations_6m", "hemoglobin_g_dl",
    "albumin_g_dl", "bmi",
]
CATEGORICAL = ["cancer_stage", "treatment_goal"]
FEATURES = NUMERIC + CATEGORICAL
TARGET_SOURCE = "on_treatment_gph"


def decline_label(baseline_gph: float, on_treatment_gph: float) -> int:
    """One when GPH falls by 10 or more points after baseline."""
    return int(on_treatment_gph - baseline_gph <= -10)

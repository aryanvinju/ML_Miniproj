"""Generate fictional patients for reproducible demonstration only."""

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def make_synthetic(n: int = 1252, seed: int = 229) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    age = np.clip(rng.normal(60, 13, n), 18, 90)
    stage = rng.choice(["I", "II", "III", "IV"], n, p=[.18, .32, .31, .19])
    goal = np.where((stage == "IV") | (rng.random(n) < .12), "palliative", "curative")
    comorb = rng.poisson(1.5 + (age > 70) * .5, n)
    ed = rng.poisson(.35 + .18 * comorb, n)
    adm = rng.binomial(2, np.clip(.07 + .07 * comorb, 0, .65), n)
    baseline_gph = np.clip(rng.normal(48 - 1.2 * comorb - .8 * (stage == "IV"), 8, n), 22, 72)
    baseline_gmh = np.clip(rng.normal(49 - .6 * comorb, 8, n), 22, 72)
    hemoglobin = np.clip(rng.normal(12.5 - .3 * (stage == "IV") - .12 * comorb, 1.5, n), 7, 17)
    albumin = np.clip(rng.normal(4 - .12 * (stage == "IV") - .04 * comorb, .42, n), 2, 5.3)
    bmi = np.clip(rng.normal(27, 5, n), 16, 48)

    # Fictional mechanism. Coefficients have no clinical interpretation.
    logit = (-1.55 + .028 * (age - 60) + .22 * comorb + .23 * ed +
             .30 * adm + .35 * (stage == "IV") - .14 * (hemoglobin - 12) -
             .55 * (albumin - 4) + .028 * (baseline_gph - 48))
    p = 1 / (1 + np.exp(-logit))
    decline = rng.binomial(1, p)
    delta = np.where(decline == 1, -10 - rng.gamma(2, 2.0, n), rng.normal(-2, 3, n))
    delta = np.where(decline == 0, np.maximum(delta, -9.9), delta)
    on_treatment = np.clip(baseline_gph + delta, 10, 80)
    frame = pd.DataFrame({
        "patient_id": [f"SYN-{i:04d}" for i in range(n)],
        "age": age.round(1), "baseline_gph": baseline_gph.round(1),
        "baseline_gmh": baseline_gmh.round(1), "comorbidity_count": comorb,
        "ed_visits_6m": ed, "hospitalizations_6m": adm,
        "hemoglobin_g_dl": hemoglobin.round(2), "albumin_g_dl": albumin.round(2),
        "bmi": bmi.round(1), "cancer_stage": stage, "treatment_goal": goal,
        "on_treatment_gph": on_treatment.round(1),
    })
    # Missing values mimic incomplete pre-treatment records. Outcomes stay observed.
    for col in ["hemoglobin_g_dl", "albumin_g_dl", "bmi", "baseline_gmh"]:
        frame.loc[rng.random(n) < .07, col] = np.nan
    return frame


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("data/synthetic_patients.csv"))
    parser.add_argument("--n", type=int, default=1252)
    parser.add_argument("--seed", type=int, default=229)
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    make_synthetic(args.n, args.seed).to_csv(args.output, index=False)
    print(f"Saved {args.n} fictional patients to {args.output}")


if __name__ == "__main__":
    main()

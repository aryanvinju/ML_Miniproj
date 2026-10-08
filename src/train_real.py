"""Train an exploratory decline model on public EORTC QLQ-C30 patient data."""

import argparse
import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, confusion_matrix, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

NUMERIC = [
    "HE_baseline", "PH_baseline", "RO_baseline", "EF_baseline",
    "COG_baseline", "SO_baseline", "FA_baseline", "Nau_baseline", "PA_baseline",
]
CATEGORICAL = ["Surgery"]
FEATURES = NUMERIC + CATEGORICAL
TARGET_COLUMNS = ["HE_baseline", "HE_end"]


def prepare_data(path: Path):
    data = pd.read_excel(path)
    needed = set(FEATURES + TARGET_COLUMNS)
    missing = needed - set(data.columns)
    if missing:
        raise ValueError(f"Workbook missing columns: {sorted(missing)}")
    # In the source, 339 rows exist; paired global-health values are observed in 217.
    paired = data.dropna(subset=TARGET_COLUMNS).copy()
    y = ((paired["HE_end"] - paired["HE_baseline"]) <= -10).astype(int)
    return paired[FEATURES], y, len(data)


def preprocessing():
    return ColumnTransformer([
        ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")),
                              ("scaler", StandardScaler())]), NUMERIC),
        ("categorical", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                                  ("onehot", OneHotEncoder(handle_unknown="ignore"))]), CATEGORICAL),
    ])


def metric_summary(y, p):
    pred = (p >= .5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "auroc": round(float(roc_auc_score(y, p)), 4),
        "average_precision": round(float(average_precision_score(y, p)), 4),
        "brier": round(float(brier_score_loss(y, p)), 4),
        "sensitivity_at_0_5": round(float(tp / (tp + fn)), 4),
        "specificity_at_0_5": round(float(tn / (tn + fp)), 4),
        "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
    }


def bootstrap_auroc_ci(y, p, n_boot=2000, seed=229):
    rng = np.random.default_rng(seed)
    y, p = np.asarray(y), np.asarray(p)
    values = []
    for _ in range(n_boot):
        idx = rng.integers(0, len(y), len(y))
        if len(np.unique(y[idx])) == 2:
            values.append(roc_auc_score(y[idx], p[idx]))
    return [round(float(v), 4) for v in np.quantile(values, [.025, .975])]


def train(path: Path, output: Path, demo_model: Path):
    X, y, source_rows = prepare_data(path)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=.2, random_state=229, stratify=y)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=229)
    candidates = {
        "logistic": Pipeline([("prep", preprocessing()),
                              ("model", LogisticRegression(C=.5, max_iter=2000))]),
        "random_forest": Pipeline([("prep", preprocessing()),
                                   ("model", RandomForestClassifier(
                                       n_estimators=300, min_samples_leaf=4, random_state=229))]),
    }
    cv_scores = {name: float(cross_val_score(model, X_train, y_train, cv=cv,
                                              scoring="roc_auc").mean())
                 for name, model in candidates.items()}
    winner = max(cv_scores, key=cv_scores.get)
    selected = candidates[winner].fit(X_train, y_train)
    p = selected.predict_proba(X_test)[:, 1]
    dummy = DummyClassifier(strategy="prior").fit(X_train, y_train)
    result = {
        "dataset": "Carmona-Bayonas et al. (2021), Figshare 10.6084/m9.figshare.14681274",
        "data_kind": "real de-identified observational cohort",
        "questionnaire": "EORTC QLQ-C30 global health status (0-100)",
        "target": "HE_end - HE_baseline <= -10 after adjuvant chemotherapy",
        "n_source": source_rows, "n_paired": len(X),
        "n_train": len(X_train), "n_test": len(X_test),
        "prevalence": round(float(y.mean()), 4),
        "test_prevalence": round(float(y_test.mean()), 4),
        "cv_auroc_mean": {k: round(v, 4) for k, v in cv_scores.items()},
        "selected_model": winner,
        "test": metric_summary(y_test, p),
        "test_auroc_bootstrap_95ci": bootstrap_auroc_ci(y_test, p),
        "dummy_test": metric_summary(y_test, dummy.predict_proba(X_test)[:, 1]),
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "real_metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    joblib.dump(selected, output / "real_model.joblib")

    # Browser always uses a logistic fit for transparent client-side inference.
    browser = candidates["logistic"].fit(X_train, y_train)
    prep = browser.named_steps["prep"]
    numeric = prep.named_transformers_["numeric"]
    encoded = prep.named_transformers_["categorical"].named_steps["onehot"]
    model = browser.named_steps["model"]
    payload = {
        "notice": "Exploratory model trained on a small public cohort; not for clinical use",
        "numeric": NUMERIC,
        "numeric_medians": numeric.named_steps["imputer"].statistics_.tolist(),
        "numeric_means": numeric.named_steps["scaler"].mean_.tolist(),
        "numeric_scales": numeric.named_steps["scaler"].scale_.tolist(),
        "categorical": CATEGORICAL,
        "categories": [list(map(str, x)) for x in encoded.categories_],
        "coefficients": model.coef_[0].tolist(),
        "intercept": float(model.intercept_[0]),
        "training_rows": len(X_train),
        "model_name": "logistic",
    }
    demo_model.parent.mkdir(parents=True, exist_ok=True)
    demo_model.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, default=Path("data/breast_qlq_c30.xlsx"))
    parser.add_argument("--output", type=Path, default=Path("models"))
    parser.add_argument("--demo-model", type=Path, default=Path("docs/model.json"))
    args = parser.parse_args()
    print(json.dumps(train(args.data, args.output, args.demo_model), indent=2))


if __name__ == "__main__":
    main()

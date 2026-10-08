"""Leakage-safe model comparison and browser export."""

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
from sklearn.metrics import (average_precision_score, brier_score_loss,
                             confusion_matrix, roc_auc_score)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .schema import CATEGORICAL, FEATURES, NUMERIC, TARGET_SOURCE


def preprocessing():
    return ColumnTransformer([
        ("numeric", Pipeline([("imputer", SimpleImputer(strategy="median")),
                              ("scaler", StandardScaler())]), NUMERIC),
        ("categorical", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")),
                                  ("onehot", OneHotEncoder(handle_unknown="ignore"))]), CATEGORICAL),
    ])


def scores(y, p):
    predicted = (p >= .5).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, predicted, labels=[0, 1]).ravel()
    return {
        "auroc": round(float(roc_auc_score(y, p)), 4),
        "average_precision": round(float(average_precision_score(y, p)), 4),
        "brier": round(float(brier_score_loss(y, p)), 4),
        "sensitivity_at_0_5": round(float(tp / (tp + fn)), 4),
        "specificity_at_0_5": round(float(tn / (tn + fp)), 4),
        "confusion_matrix": [[int(tn), int(fp)], [int(fn), int(tp)]],
    }


def train(data: pd.DataFrame, output: Path, demo_model: Path) -> dict:
    missing = set(FEATURES + [TARGET_SOURCE]) - set(data.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")
    data = data.dropna(subset=["baseline_gph", TARGET_SOURCE]).copy()
    if len(data) < 100:
        raise ValueError("At least 100 complete outcomes are required for this example split")
    y = ((data[TARGET_SOURCE] - data["baseline_gph"]) <= -10).astype(int)
    if y.nunique() != 2 or y.value_counts().min() < 10:
        raise ValueError("Both target classes need at least 10 examples")
    X = data[FEATURES]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=.2, random_state=229, stratify=y)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=229)
    candidates = {
        "logistic": Pipeline([("prep", preprocessing()),
                              ("model", LogisticRegression(C=.5, max_iter=2000))]),
        "random_forest": Pipeline([("prep", preprocessing()),
                                   ("model", RandomForestClassifier(n_estimators=300,
                                                                      min_samples_leaf=5,
                                                                      random_state=229))]),
    }
    cv_scores = {name: float(cross_val_score(model, X_train, y_train, cv=cv,
                                              scoring="roc_auc").mean())
                 for name, model in candidates.items()}
    winner = max(cv_scores, key=cv_scores.get)
    selected = candidates[winner].fit(X_train, y_train)
    prior = DummyClassifier(strategy="prior").fit(X_train, y_train)
    result = {
        "data_kind": "synthetic only unless a user-provided dataset was supplied",
        "target": "on_treatment_gph - baseline_gph <= -10",
        "n_total": int(len(data)), "n_train": int(len(X_train)),
        "n_test": int(len(X_test)), "prevalence": round(float(y.mean()), 4),
        "cv_auroc_mean": {k: round(v, 4) for k, v in cv_scores.items()},
        "selected_model": winner,
        "test": scores(y_test, selected.predict_proba(X_test)[:, 1]),
        "dummy_test": scores(y_test, prior.predict_proba(X_test)[:, 1]),
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "metrics.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    joblib.dump(selected, output / "model.joblib")

    # The browser demo uses a separate logistic fit so its coefficients remain auditable.
    browser = candidates["logistic"].fit(X_train, y_train)
    prep = browser.named_steps["prep"]
    numeric = prep.named_transformers_["numeric"]
    encoded = prep.named_transformers_["categorical"].named_steps["onehot"]
    model = browser.named_steps["model"]
    payload = {
        "notice": "Synthetic educational model; not for clinical use",
        "numeric": NUMERIC,
        "numeric_medians": numeric.named_steps["imputer"].statistics_.tolist(),
        "numeric_means": numeric.named_steps["scaler"].mean_.tolist(),
        "numeric_scales": numeric.named_steps["scaler"].scale_.tolist(),
        "categorical": CATEGORICAL,
        "categories": [list(map(str, x)) for x in encoded.categories_],
        "coefficients": model.coef_[0].tolist(),
        "intercept": float(model.intercept_[0]),
        "training_rows": int(len(X_train)),
    }
    demo_model.parent.mkdir(parents=True, exist_ok=True)
    demo_model.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("models"))
    parser.add_argument("--demo-model", type=Path, default=Path("docs/model.json"))
    args = parser.parse_args()
    result = train(pd.read_csv(args.data), args.output, args.demo_model)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.train_real import FEATURES, prepare_data, train

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "breast_qlq_c30.xlsx"


def test_public_cohort_and_target_definition():
    X, y, n_source = prepare_data(DATA)
    assert n_source == 339
    assert len(X) == 217
    assert int(y.sum()) == 78
    assert not any("_end" in feature for feature in FEATURES)
    raw = pd.read_excel(DATA).dropna(subset=["HE_baseline", "HE_end"])
    assert np.array_equal(y.to_numpy(), ((raw.HE_end - raw.HE_baseline) <= -10).astype(int).to_numpy())


def test_training_and_browser_export(tmp_path):
    metrics = train(DATA, tmp_path / "models", tmp_path / "docs" / "model.json")
    assert metrics["n_test"] == 44
    assert metrics["selected_model"] == "logistic"
    assert 0 <= metrics["test"]["auroc"] <= 1
    browser = json.loads((tmp_path / "docs" / "model.json").read_text())
    assert browser["numeric"] == FEATURES[:-1]
    assert len(browser["coefficients"]) == len(browser["numeric"]) + sum(map(len, browser["categories"]))

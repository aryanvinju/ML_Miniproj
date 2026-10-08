from src.generate_data import make_synthetic
from src.schema import decline_label
from src.train import train


def test_decline_boundary():
    assert decline_label(50, 40) == 1
    assert decline_label(50, 40.1) == 0


def test_training_writes_outputs(tmp_path):
    data = make_synthetic(300)
    result = train(data, tmp_path / "models", tmp_path / "docs" / "model.json")
    assert result["n_test"] == 60
    assert 0 <= result["test"]["auroc"] <= 1
    assert (tmp_path / "docs" / "model.json").exists()

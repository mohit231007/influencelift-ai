from pathlib import Path

from influencelift.demo_data import generate_demo_dataset
from influencelift.inference import ModelBundle, load_bundle, predict_campaigns
from influencelift.modeling import save_bundle, train_bundle


def test_training_and_prediction_round_trip(tmp_path: Path):
    frame = generate_demo_dataset(rows=250, seed=7, messy=True)
    payload = train_bundle(frame, folds=3, model_version="test")
    path = save_bundle(payload, tmp_path / "model.joblib")
    bundle = load_bundle(path)

    assert isinstance(bundle, ModelBundle)
    predictions = predict_campaigns(bundle, frame.head(5))
    assert len(predictions) == 5
    assert (predictions["Predicted_Sales_Units"] >= 0).all()
    assert (predictions["Prediction_Upper_95"] >= predictions["Prediction_Lower_95"]).all()
    assert payload["metrics"]["r2"] > 0.2

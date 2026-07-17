from fastapi.testclient import TestClient

from api.main import app, get_bundle

client = TestClient(app)


def setup_function():
    get_bundle.cache_clear()


def test_health_endpoint():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_predict_accepts_messy_values(tmp_path, monkeypatch):
    monkeypatch.setenv("MODEL_PATH", str(tmp_path / "model.joblib"))
    response = client.post(
        "/predict",
        json={
            "followers": "125K",
            "engagement_rate": "3.7%",
            "ad_spend": "£5,500",
            "content_quality": 8.2,
        },
    )
    assert response.status_code == 200
    payload = response.json()
    assert payload["predicted_sales_units"] >= 0
    assert "followers_explicit_scale_parsed" in payload["corrections_applied"]

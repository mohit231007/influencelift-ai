"""FastAPI service for InfluenceLift AI."""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

import pandas as pd
from fastapi import FastAPI, HTTPException

from api.schemas import (
    BatchPredictionRequest,
    BatchPredictionResponse,
    CampaignRequest,
    PredictionResponse,
)
from influencelift.cleaning import audit_campaign_data, audit_row_corrections
from influencelift.inference import ModelBundle, load_or_create_bundle, predict_campaigns

app = FastAPI(
    title="InfluenceLift AI API",
    version="1.0.0",
    description="Forecast sales from messy influencer-campaign attributes.",
)


@lru_cache(maxsize=1)
def get_bundle() -> ModelBundle:
    model_path = Path(os.getenv("MODEL_PATH", "artifacts/model_bundle.joblib"))
    return load_or_create_bundle(model_path)


def _response_for(request: CampaignRequest) -> PredictionResponse:
    frame = pd.DataFrame([request.to_raw_record()])
    bundle = get_bundle()
    try:
        prediction = predict_campaigns(bundle, frame).iloc[0]
        report = audit_campaign_data(frame)
        corrections = audit_row_corrections(frame)[0]
    except (TypeError, ValueError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    warnings = [
        warning
        for warning in str(prediction["Extrapolation_Warnings"]).split(", ")
        if warning
    ]
    return PredictionResponse(
        predicted_sales_units=int(prediction["Predicted_Sales_Units"]),
        prediction_lower_bound=int(prediction["Prediction_Lower_95"]),
        prediction_upper_bound=int(prediction["Prediction_Upper_95"]),
        data_quality_status=report.status,
        corrections_applied=corrections,
        extrapolation_warnings=warnings,
        model_version=bundle.model_version,
    )


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/model-info")
def model_info() -> dict:
    bundle = get_bundle()
    return {
        "model_version": bundle.model_version,
        "alpha": bundle.alpha,
        "metrics": bundle.metrics,
        "training_ranges": bundle.training_ranges,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict(request: CampaignRequest) -> PredictionResponse:
    return _response_for(request)


@app.post("/predict-batch", response_model=BatchPredictionResponse)
def predict_batch(request: BatchPredictionRequest) -> BatchPredictionResponse:
    if not request.campaigns:
        raise HTTPException(status_code=422, detail="At least one campaign is required.")
    return BatchPredictionResponse(predictions=[_response_for(item) for item in request.campaigns])

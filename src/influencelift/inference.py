"""Model loading, prediction, uncertainty, and extrapolation checks."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd

from influencelift.cleaning import (
    audit_campaign_data,
    audit_row_corrections,
    clean_campaign_frame,
)
from influencelift.demo_data import generate_demo_dataset
from influencelift.modeling import save_bundle, train_bundle

DEFAULT_MODEL_PATH = Path(os.getenv("MODEL_PATH", "artifacts/model_bundle.joblib"))


@dataclass
class ModelBundle:
    pipeline: Any
    residual_quantile_95: float
    metrics: dict[str, Any]
    training_ranges: dict[str, dict[str, float]]
    model_version: str
    alpha: float

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> ModelBundle:
        return cls(
            pipeline=payload["pipeline"],
            residual_quantile_95=float(payload.get("residual_quantile_95", 0.0)),
            metrics=dict(payload.get("metrics", {})),
            training_ranges=dict(payload.get("training_ranges", {})),
            model_version=str(payload.get("model_version", "unknown")),
            alpha=float(payload.get("alpha", 1.0)),
        )


def load_bundle(path: str | Path = DEFAULT_MODEL_PATH) -> ModelBundle:
    return ModelBundle.from_dict(joblib.load(path))


def load_or_create_bundle(path: str | Path = DEFAULT_MODEL_PATH) -> ModelBundle:
    """Load a trained bundle or create a deterministic demo bundle for first run."""

    model_path = Path(path)
    if model_path.exists():
        return load_bundle(model_path)

    demo = generate_demo_dataset(rows=1200, seed=42, messy=True)
    payload = train_bundle(demo, model_version="demo-1.0.0")
    save_bundle(payload, model_path)
    return ModelBundle.from_dict(payload)


def _extrapolation_flags(bundle: ModelBundle, frame: pd.DataFrame) -> list[list[str]]:
    cleaned = clean_campaign_frame(frame)
    output: list[list[str]] = []
    for _, row in cleaned.iterrows():
        flags: list[str] = []
        for column, limits in bundle.training_ranges.items():
            value = row.get(column)
            if pd.isna(value):
                continue
            if value < limits["min"] or value > limits["max"]:
                flags.append(f"{column}_outside_training_range")
        output.append(flags)
    return output


def predict_campaigns(bundle: ModelBundle, frame: pd.DataFrame) -> pd.DataFrame:
    raw_predictions = np.asarray(bundle.pipeline.predict(frame), dtype=float)
    predictions = np.clip(raw_predictions, 0, None)
    interval = max(float(bundle.residual_quantile_95), 0.0)
    corrections = audit_row_corrections(frame)
    extrapolation = _extrapolation_flags(bundle, frame)

    result = pd.DataFrame(index=frame.index)
    if "ID" in frame.columns:
        result["ID"] = pd.to_numeric(frame["ID"], errors="coerce").astype("Int64")
    result["Predicted_Sales_Units"] = np.rint(predictions).astype(int)
    result["Prediction_Lower_95"] = np.rint(np.clip(predictions - interval, 0, None)).astype(int)
    result["Prediction_Upper_95"] = np.rint(predictions + interval).astype(int)
    result["Corrections_Applied"] = [", ".join(flags) for flags in corrections]
    result["Extrapolation_Warnings"] = [", ".join(flags) for flags in extrapolation]
    return result.reset_index(drop=True)


def prediction_metadata(bundle: ModelBundle, frame: pd.DataFrame) -> dict[str, Any]:
    report = audit_campaign_data(frame)
    return {
        "model_version": bundle.model_version,
        "model_metrics": bundle.metrics,
        "data_quality": report.to_dict(),
    }

"""Training and cross-validation utilities."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, cross_val_predict
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from influencelift.cleaning import CampaignCleaner, CleaningPolicy, parse_human_number

TARGET_COLUMN = "Sales (Units)"


@dataclass
class EvaluationMetrics:
    rmse: float
    mae: float
    r2: float
    residual_quantile_95: float
    rows: int
    folds: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def build_pipeline(
    alpha: float = 1.0,
    policy: CleaningPolicy | None = None,
) -> Pipeline:
    return Pipeline(
        steps=[
            ("cleaner", CampaignCleaner(policy=policy)),
            ("imputer", SimpleImputer(strategy="median", add_indicator=True)),
            ("scaler", StandardScaler()),
            ("model", Ridge(alpha=alpha)),
        ]
    )


def extract_target(frame: pd.DataFrame) -> pd.Series:
    if TARGET_COLUMN not in frame.columns:
        raise ValueError(f"Training data must contain '{TARGET_COLUMN}'.")
    target = frame[TARGET_COLUMN].map(parse_human_number).astype(float)
    if target.isna().any():
        count = int(target.isna().sum())
        raise ValueError(f"Target contains {count} missing or non-numeric values.")
    if (target < 0).any():
        raise ValueError("Target contains negative sales values.")
    return target


def evaluate_pipeline(
    frame: pd.DataFrame,
    pipeline: Pipeline | None = None,
    folds: int = 5,
    random_state: int = 42,
) -> tuple[EvaluationMetrics, np.ndarray]:
    target = extract_target(frame)
    pipeline = pipeline or build_pipeline()
    splitter = KFold(n_splits=folds, shuffle=True, random_state=random_state)
    predictions = cross_val_predict(pipeline, frame, target, cv=splitter, n_jobs=None)
    predictions = np.clip(predictions, 0, None)
    residuals = np.abs(target.to_numpy() - predictions)

    metrics = EvaluationMetrics(
        rmse=float(mean_squared_error(target, predictions) ** 0.5),
        mae=float(mean_absolute_error(target, predictions)),
        r2=float(r2_score(target, predictions)),
        residual_quantile_95=float(np.quantile(residuals, 0.95)),
        rows=len(frame),
        folds=folds,
    )
    return metrics, predictions


def train_bundle(
    frame: pd.DataFrame,
    alpha: float = 1.0,
    folds: int = 5,
    random_state: int = 42,
    model_version: str = "1.0.0",
) -> dict[str, Any]:
    pipeline = build_pipeline(alpha=alpha)
    metrics, _ = evaluate_pipeline(
        frame,
        pipeline=pipeline,
        folds=folds,
        random_state=random_state,
    )
    target = extract_target(frame)
    pipeline.fit(frame, target)

    cleaned = pipeline.named_steps["cleaner"].transform(frame)
    training_ranges = {
        column: {
            "min": float(cleaned[column].min(skipna=True)),
            "max": float(cleaned[column].max(skipna=True)),
        }
        for column in cleaned.columns
    }

    return {
        "pipeline": pipeline,
        "metrics": metrics.to_dict(),
        "residual_quantile_95": metrics.residual_quantile_95,
        "training_ranges": training_ranges,
        "model_version": model_version,
        "alpha": alpha,
    }


def save_bundle(bundle: dict[str, Any], path: str | Path) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(bundle, destination)
    return destination

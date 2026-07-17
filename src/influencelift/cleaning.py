"""Parsing, validation, and auditable cleaning for campaign data."""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin

RAW_FEATURE_COLUMNS = [
    "Followers",
    "EngagementRate (%)",
    "AdSpend (GBP)",
    "ContentQuality",
]
MODEL_FEATURE_COLUMNS = ["Followers", "EngagementRate", "AdSpend", "ContentQuality"]

_MISSING_TEXT = {"", "nan", "none", "null", "n/a", "na", "-"}


@dataclass(frozen=True)
class CleaningPolicy:
    """Configuration for transparent, dataset-specific repair rules."""

    infer_small_followers_as_thousands: bool = True
    small_follower_threshold: float = 1_000.0
    repair_inflated_followers: bool = True
    inflated_follower_threshold: float = 1_000_000.0
    inflated_follower_divisor: float = 10_000.0
    repair_inflated_spend: bool = True
    inflated_spend_threshold: float = 100_000.0
    inflated_spend_divisor: float = 100_000.0
    absolute_negative_engagement: bool = True
    absolute_negative_spend: bool = True
    content_quality_min: float = 1.0
    content_quality_max: float = 10.0


@dataclass
class DataQualityReport:
    rows: int
    missing_by_column: dict[str, int]
    correction_counts: dict[str, int]
    invalid_counts: dict[str, int]
    status: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def validate_required_columns(frame: pd.DataFrame) -> None:
    if not isinstance(frame, pd.DataFrame):
        raise TypeError("Expected a pandas DataFrame.")
    missing = [column for column in RAW_FEATURE_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _normalise_text(value: Any) -> str | None:
    if value is None or pd.isna(value):
        return None
    text = str(value).strip()
    if text.lower() in _MISSING_TEXT:
        return None
    return text


def parse_human_number(value: Any) -> float:
    """Parse currency, percentages, commas, and K/M/B suffixes into a float."""

    text = _normalise_text(value)
    if text is None:
        return np.nan

    text = text.replace(",", "")
    text = re.sub(r"[£$€₹%\s]", "", text)
    match = re.fullmatch(r"([+-]?(?:\d+(?:\.\d*)?|\.\d+))([kKmMbB]?)", text)
    if not match:
        return np.nan

    number = float(match.group(1))
    scale = {"": 1.0, "k": 1_000.0, "m": 1_000_000.0, "b": 1_000_000_000.0}
    return number * scale[match.group(2).lower()]


def _parse_series(series: pd.Series) -> pd.Series:
    return series.map(parse_human_number).astype(float)


def clean_campaign_frame(
    frame: pd.DataFrame,
    policy: CleaningPolicy | None = None,
) -> pd.DataFrame:
    """Return the four numeric features consumed by the production model."""

    validate_required_columns(frame)
    policy = policy or CleaningPolicy()

    followers = _parse_series(frame["Followers"])
    if policy.infer_small_followers_as_thousands:
        followers = followers.mask(
            followers.notna() & (followers.abs() < policy.small_follower_threshold),
            followers * 1_000.0,
        )
    if policy.repair_inflated_followers:
        followers = followers.mask(
            followers.abs() > policy.inflated_follower_threshold,
            followers / policy.inflated_follower_divisor,
        )
    followers = followers.mask(followers < 0)

    engagement = _parse_series(frame["EngagementRate (%)"])
    if policy.absolute_negative_engagement:
        engagement = engagement.abs()
    engagement = engagement.mask(engagement > 100)

    spend = _parse_series(frame["AdSpend (GBP)"])
    if policy.absolute_negative_spend:
        spend = spend.abs()
    if policy.repair_inflated_spend:
        spend = spend.mask(
            spend > policy.inflated_spend_threshold,
            spend / policy.inflated_spend_divisor,
        )

    content_quality = _parse_series(frame["ContentQuality"])
    content_quality = content_quality.mask(
        (content_quality < policy.content_quality_min)
        | (content_quality > policy.content_quality_max)
    )

    return pd.DataFrame(
        {
            "Followers": followers,
            "EngagementRate": engagement,
            "AdSpend": spend,
            "ContentQuality": content_quality,
        },
        index=frame.index,
        dtype=float,
    )


def audit_row_corrections(
    frame: pd.DataFrame,
    policy: CleaningPolicy | None = None,
) -> list[list[str]]:
    """Return correction and validation flags for each row."""

    validate_required_columns(frame)
    policy = policy or CleaningPolicy()
    results: list[list[str]] = []

    for _, row in frame.iterrows():
        issues: list[str] = []
        follower_text = _normalise_text(row["Followers"])
        engagement_text = _normalise_text(row["EngagementRate (%)"])
        spend_text = _normalise_text(row["AdSpend (GBP)"])

        follower = parse_human_number(row["Followers"])
        engagement = parse_human_number(row["EngagementRate (%)"])
        spend = parse_human_number(row["AdSpend (GBP)"])
        quality = parse_human_number(row["ContentQuality"])

        if follower_text and follower_text[-1:].lower() in {"k", "m", "b"}:
            issues.append("followers_explicit_scale_parsed")
        if pd.notna(follower) and abs(follower) < policy.small_follower_threshold:
            issues.append("followers_inferred_as_thousands")
        if pd.notna(follower) and abs(follower) > policy.inflated_follower_threshold:
            issues.append("followers_inflated_scale_repaired")
        if pd.notna(follower) and follower < 0:
            issues.append("followers_negative_invalid")

        if engagement_text and "%" in engagement_text:
            issues.append("engagement_percentage_symbol_removed")
        if pd.notna(engagement) and engagement < 0:
            issues.append("engagement_negative_sign_repaired")
        if pd.notna(engagement) and abs(engagement) > 100:
            issues.append("engagement_out_of_range_invalid")

        if spend_text and re.search(r"[£$€₹]", spend_text):
            issues.append("spend_currency_symbol_removed")
        if pd.notna(spend) and spend < 0:
            issues.append("spend_negative_sign_repaired")
        if pd.notna(spend) and abs(spend) > policy.inflated_spend_threshold:
            issues.append("spend_inflated_scale_repaired")

        if pd.notna(quality) and not (
            policy.content_quality_min <= quality <= policy.content_quality_max
        ):
            issues.append("content_quality_out_of_range_invalid")

        for column in RAW_FEATURE_COLUMNS:
            if _normalise_text(row[column]) is None:
                issues.append(f"{column}_missing")

        results.append(issues)
    return results


def audit_campaign_data(
    frame: pd.DataFrame,
    policy: CleaningPolicy | None = None,
) -> DataQualityReport:
    validate_required_columns(frame)
    policy = policy or CleaningPolicy()
    row_flags = audit_row_corrections(frame, policy)
    flat_flags = [flag for flags in row_flags for flag in flags]

    correction_prefixes = (
        "followers_explicit",
        "followers_inferred",
        "followers_inflated",
        "engagement_percentage",
        "engagement_negative",
        "spend_currency",
        "spend_negative",
        "spend_inflated",
    )
    invalid_fragments = ("invalid", "missing")

    corrections = sorted({flag for flag in flat_flags if flag.startswith(correction_prefixes)})
    invalid = sorted({flag for flag in flat_flags if any(x in flag for x in invalid_fragments)})

    correction_counts = {flag: flat_flags.count(flag) for flag in corrections}
    invalid_counts = {flag: flat_flags.count(flag) for flag in invalid}
    missing_by_column = {column: int(frame[column].isna().sum()) for column in RAW_FEATURE_COLUMNS}

    if invalid_counts:
        status = "requires_review"
    elif correction_counts:
        status = "valid_with_corrections"
    else:
        status = "valid"

    return DataQualityReport(
        rows=len(frame),
        missing_by_column=missing_by_column,
        correction_counts=correction_counts,
        invalid_counts=invalid_counts,
        status=status,
    )


class CampaignCleaner(BaseEstimator, TransformerMixin):
    """Scikit-learn transformer that keeps cleaning inside the model pipeline."""

    def __init__(self, policy: CleaningPolicy | None = None):
        self.policy = policy

    def fit(self, X: pd.DataFrame, y: pd.Series | None = None) -> CampaignCleaner:
        validate_required_columns(X)
        return self

    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        return clean_campaign_frame(X, self.policy)

    def get_feature_names_out(self, input_features: Any = None) -> np.ndarray:
        return np.asarray(MODEL_FEATURE_COLUMNS, dtype=object)

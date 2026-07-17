"""Deterministic synthetic campaign data for public demos and tests."""

from __future__ import annotations

import numpy as np
import pandas as pd


def generate_demo_dataset(
    rows: int = 1000,
    seed: int = 42,
    messy: bool = True,
) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    followers = np.clip(rng.normal(95_000, 35_000, rows), 8_000, 250_000)
    engagement = rng.uniform(0.5, 5.0, rows)
    spend = np.clip(rng.normal(4_800, 1_600, rows), 500, 12_000)
    quality = rng.uniform(1.0, 10.0, rows)
    noise = rng.normal(0, 2_000, rows)

    sales = (
        450
        + 0.050 * followers
        + 180 * engagement
        + 0.79 * spend
        + 190 * quality
        + noise
    )
    sales = np.rint(np.clip(sales, 0, None)).astype(int)

    frame = pd.DataFrame(
        {
            "Followers": followers.round(0),
            "EngagementRate (%)": engagement.round(3),
            "AdSpend (GBP)": spend.round(2),
            "ContentQuality": quality.round(2),
            "Sales (Units)": sales,
            "ID": np.arange(1, rows + 1),
            "Timestamp": pd.date_range("2023-01-01", periods=rows, freq="D"),
            "Notes": rng.choice(["Good", "Review", "Pending", "Check", None], rows),
        }
    )

    if not messy or rows == 0:
        return frame

    # Object dtype is intentional: public demo rows mix numeric and formatted strings.
    for column in ["Followers", "EngagementRate (%)", "AdSpend (GBP)"]:
        frame[column] = frame[column].astype(object)

    sample_size = max(1, rows // 25)
    index = frame.index.to_numpy()

    percent_idx = rng.choice(index, sample_size, replace=False)
    frame.loc[percent_idx, "EngagementRate (%)"] = frame.loc[
        percent_idx, "EngagementRate (%)"
    ].map(lambda value: f"{value}%")

    currency_idx = rng.choice(index, sample_size, replace=False)
    frame.loc[currency_idx, "AdSpend (GBP)"] = frame.loc[currency_idx, "AdSpend (GBP)"].map(
        lambda value: f"£{float(value):,.0f}"
    )

    k_idx = rng.choice(index, sample_size, replace=False)
    frame.loc[k_idx, "Followers"] = frame.loc[k_idx, "Followers"].map(
        lambda value: f"{float(value) / 1_000:.1f}K"
    )

    small_idx = rng.choice(index, sample_size, replace=False)
    frame.loc[small_idx, "Followers"] = (
        pd.to_numeric(frame.loc[small_idx, "Followers"], errors="coerce") / 1_000
    ).round(0)

    missing_idx = rng.choice(index, sample_size, replace=False)
    frame.loc[missing_idx, "ContentQuality"] = np.nan

    negative_idx = rng.choice(index, sample_size, replace=False)
    frame.loc[negative_idx, "AdSpend (GBP)"] = -pd.to_numeric(
        frame.loc[negative_idx, "AdSpend (GBP)"], errors="coerce"
    )

    return frame

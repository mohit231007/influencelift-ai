"""Pydantic request and response contracts."""

from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

Scalar = str | float | int | None


class CampaignRequest(BaseModel):
    model_config = ConfigDict(json_schema_extra={
        "example": {
            "followers": "125K",
            "engagement_rate": "3.7%",
            "ad_spend": "£5,500",
            "content_quality": 8.2,
            "timestamp": "2026-07-17",
        }
    })

    followers: Scalar = Field(description="Influencer follower count; K/M suffixes are accepted.")
    engagement_rate: Scalar = Field(description="Engagement rate in percentage points.")
    ad_spend: Scalar = Field(description="Campaign spend in GBP; currency symbols are accepted.")
    content_quality: Scalar = Field(description="Subjective content-quality score from 1 to 10.")
    timestamp: date | None = None
    campaign_id: int | None = None

    def to_raw_record(self) -> dict[str, Any]:
        return {
            "Followers": self.followers,
            "EngagementRate (%)": self.engagement_rate,
            "AdSpend (GBP)": self.ad_spend,
            "ContentQuality": self.content_quality,
            "Timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "ID": self.campaign_id,
        }


class PredictionResponse(BaseModel):
    predicted_sales_units: int
    prediction_lower_bound: int
    prediction_upper_bound: int
    data_quality_status: str
    corrections_applied: list[str]
    extrapolation_warnings: list[str]
    model_version: str


class BatchPredictionRequest(BaseModel):
    campaigns: list[CampaignRequest]


class BatchPredictionResponse(BaseModel):
    predictions: list[PredictionResponse]

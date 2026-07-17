"""InfluenceLift AI package."""

from influencelift.cleaning import CampaignCleaner, CleaningPolicy, audit_campaign_data
from influencelift.inference import ModelBundle, load_or_create_bundle, predict_campaigns
from influencelift.modeling import build_pipeline, evaluate_pipeline, train_bundle

__all__ = [
    "CampaignCleaner",
    "CleaningPolicy",
    "ModelBundle",
    "audit_campaign_data",
    "build_pipeline",
    "evaluate_pipeline",
    "load_or_create_bundle",
    "predict_campaigns",
    "train_bundle",
]

__version__ = "1.0.0"

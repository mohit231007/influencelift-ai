import numpy as np
import pandas as pd
import pytest

from influencelift.cleaning import (
    CampaignCleaner,
    audit_campaign_data,
    clean_campaign_frame,
    parse_human_number,
)


def test_parse_human_number_supports_common_formats():
    assert parse_human_number("£5,000") == 5000
    assert parse_human_number("3.2%") == 3.2
    assert parse_human_number("125K") == 125000
    assert parse_human_number("1.4M") == 1400000
    assert np.isnan(parse_human_number("not-a-number"))


def test_cleaner_repairs_case_study_formats():
    frame = pd.DataFrame(
        {
            "Followers": [125, 2_000_000_000],
            "EngagementRate (%)": ["-3.2%", 2.5],
            "AdSpend (GBP)": ["£5,000", -7000],
            "ContentQuality": [8, 15],
        }
    )
    cleaned = clean_campaign_frame(frame)
    assert cleaned.loc[0, "Followers"] == 125000
    assert cleaned.loc[1, "Followers"] == 200000
    assert cleaned.loc[0, "EngagementRate"] == 3.2
    assert cleaned.loc[1, "AdSpend"] == 7000
    assert np.isnan(cleaned.loc[1, "ContentQuality"])


def test_audit_reports_corrections():
    frame = pd.DataFrame(
        {
            "Followers": ["125K"],
            "EngagementRate (%)": ["3.2%"],
            "AdSpend (GBP)": ["£5,000"],
            "ContentQuality": [8],
        }
    )
    report = audit_campaign_data(frame)
    assert report.status == "valid_with_corrections"
    assert report.correction_counts["followers_explicit_scale_parsed"] == 1


def test_cleaner_rejects_missing_schema():
    with pytest.raises(ValueError, match="Missing required columns"):
        CampaignCleaner().fit(pd.DataFrame({"Followers": [1000]}))

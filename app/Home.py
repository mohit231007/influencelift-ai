"""Streamlit application for campaign forecasting and scenario analysis."""

from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from influencelift.cleaning import audit_campaign_data
from influencelift.inference import load_or_create_bundle, predict_campaigns
from influencelift.simulation import compare_scenarios

st.set_page_config(page_title="InfluenceLift AI", page_icon="📈", layout="wide")

CORRECTION_LABELS = {
    "followers_explicit_scale_parsed": "Converted the follower abbreviation to a full number",
    "followers_inferred_as_thousands": "Interpreted a small follower value as thousands",
    "followers_extreme_scale_repaired": "Repaired an implausibly large follower scale",
    "engagement_percentage_symbol_removed": "Removed the percentage symbol from engagement rate",
    "engagement_negative_sign_repaired": "Repaired a negative engagement-rate sign",
    "spend_currency_symbol_removed": "Removed the currency symbol from ad spend",
    "spend_negative_sign_repaired": "Repaired a negative ad-spend sign",
    "spend_extreme_scale_repaired": "Repaired an implausibly large ad-spend scale",
    "ContentQuality_missing": "Content quality was missing and was imputed by the model",
}

STATUS_LABELS = {
    "valid": "Valid",
    "valid_with_corrections": "Valid after automatic corrections",
    "requires_review": "Requires review",
}


@st.cache_resource
def model_bundle():
    return load_or_create_bundle()


def _split_flags(value: Any) -> list[str]:
    if value is None or pd.isna(value):
        return []
    return [flag.strip() for flag in str(value).split(",") if flag.strip()]


def _friendly_flags(value: Any) -> list[str]:
    return [
        CORRECTION_LABELS.get(flag, flag.replace("_", " ").strip().capitalize())
        for flag in _split_flags(value)
    ]


def _status_label(status: str) -> str:
    return STATUS_LABELS.get(status, status.replace("_", " ").title())


bundle = model_bundle()

st.title("InfluenceLift AI")
st.subheader("Predict influencer campaign sales before the budget is spent.")
st.caption(
    "A production-style demonstration of messy-data cleaning, regression, uncertainty, "
    "and marketing scenario analysis."
)

link_col, spacer_col = st.columns([1, 4])
with link_col:
    st.link_button(
        "View source on GitHub",
        "https://github.com/mohit231007/influencelift-ai",
        use_container_width=True,
    )
with spacer_col:
    st.caption(
        "Public demo predictions use a deterministic synthetic training set because the original "
        "challenge data is not redistributed."
    )

metric_columns = st.columns(4)
metric_columns[0].metric("Selected model", "Ridge")
metric_columns[1].metric("Original case-study RMSE", "2,000")
metric_columns[2].metric("Original case-study R²", "0.493")
metric_columns[3].metric("Loaded demo version", bundle.model_version)

st.info(
    "The benchmark metrics above come from the original case-study dataset. "
    "The live app loads a synthetic demo model, so the metrics shown under Model information "
    "will differ."
)

predictor_tab, batch_tab, simulator_tab, model_tab = st.tabs(
    ["Campaign predictor", "Batch predictions", "Scenario simulator", "Model information"]
)

with predictor_tab:
    st.markdown("### Forecast a single campaign")
    st.caption("Messy formats such as `125K`, `3.7%`, and `£5,500` are accepted directly.")
    left, right = st.columns(2)
    with left:
        followers = st.text_input("Followers", value="125K")
        engagement = st.text_input("Engagement rate", value="3.7%")
    with right:
        spend = st.text_input("Ad spend (GBP)", value="£5,500")
        quality = st.slider("Content quality", min_value=1.0, max_value=10.0, value=8.2, step=0.1)

    record = pd.DataFrame(
        [
            {
                "Followers": followers,
                "EngagementRate (%)": engagement,
                "AdSpend (GBP)": spend,
                "ContentQuality": quality,
            }
        ]
    )

    if st.button("Predict sales", type="primary", use_container_width=True):
        prediction = predict_campaigns(bundle, record).iloc[0]
        report = audit_campaign_data(record)
        a, b, c = st.columns(3)
        a.metric("Predicted sales", f"{prediction['Predicted_Sales_Units']:,} units")
        b.metric("95% lower estimate", f"{prediction['Prediction_Lower_95']:,}")
        c.metric("95% upper estimate", f"{prediction['Prediction_Upper_95']:,}")

        status_text = _status_label(report.status)
        if report.status == "requires_review":
            st.warning(f"Data-quality status: **{status_text}**")
        else:
            st.success(f"Data-quality status: **{status_text}**")

        corrections = _friendly_flags(prediction["Corrections_Applied"])
        if corrections:
            st.markdown("**Automatic corrections applied**")
            for correction in corrections:
                st.markdown(f"- {correction}")

        warnings = _friendly_flags(prediction["Extrapolation_Warnings"])
        if warnings:
            st.warning("Prediction reliability warning:\n\n" + "\n".join(f"- {item}" for item in warnings))

        st.caption(
            "The interval reflects historical model error. It is not a guarantee, and campaign "
            "changes should not be interpreted as causal effects."
        )

with batch_tab:
    st.markdown("### Upload campaign data")
    st.caption("Upload a CSV to audit data quality and generate campaign-level forecasts.")
    uploaded = st.file_uploader("CSV file", type=["csv"])
    if uploaded is None:
        st.code(
            "Followers,EngagementRate (%),AdSpend (GBP),ContentQuality,ID\n"
            "125K,3.7%,£5500,8.2,1"
        )
    else:
        uploaded_frame = pd.read_csv(uploaded)
        st.markdown("#### Input preview")
        st.dataframe(uploaded_frame.head(20), use_container_width=True)
        try:
            report = audit_campaign_data(uploaded_frame)
            report_data = report.to_dict()
            total_missing = sum(report_data.get("missing_by_column", {}).values())
            total_corrections = sum(report_data.get("correction_counts", {}).values())

            status_col, row_col, missing_col, correction_col = st.columns(4)
            status_col.metric("Data status", _status_label(report.status))
            row_col.metric("Rows received", f"{len(uploaded_frame):,}")
            missing_col.metric("Missing cells", f"{total_missing:,}")
            correction_col.metric("Corrections detected", f"{total_corrections:,}")

            if report.status == "requires_review":
                st.warning(
                    "At least one field requires review. Predictions are still generated where "
                    "the model can safely impute missing values."
                )

            with st.expander("View detailed data-quality audit"):
                st.json(report_data)

            predictions = predict_campaigns(bundle, uploaded_frame)
            st.markdown("#### Prediction results")
            st.dataframe(predictions, use_container_width=True)
            st.download_button(
                "Download predictions",
                data=predictions.to_csv(index=False).encode("utf-8"),
                file_name="influencelift_predictions.csv",
                mime="text/csv",
                use_container_width=True,
            )
        except (TypeError, ValueError) as exc:
            st.error(str(exc))

with simulator_tab:
    st.markdown("### Compare a baseline and proposed campaign")
    st.caption(
        "Use the scenario simulator to compare configurations before committing campaign budget."
    )
    baseline_col, proposed_col = st.columns(2)
    with baseline_col:
        st.markdown("#### Baseline")
        base_followers = st.number_input("Baseline followers", 1_000, 5_000_000, 100_000, 1_000)
        base_engagement = st.number_input("Baseline engagement (%)", 0.0, 100.0, 2.5, 0.1)
        base_spend = st.number_input("Baseline spend (£)", 0.0, 1_000_000.0, 4_000.0, 100.0)
        base_quality = st.number_input("Baseline quality", 1.0, 10.0, 6.0, 0.1)
    with proposed_col:
        st.markdown("#### Proposed")
        new_followers = st.number_input("Proposed followers", 1_000, 5_000_000, 125_000, 1_000)
        new_engagement = st.number_input("Proposed engagement (%)", 0.0, 100.0, 3.5, 0.1)
        new_spend = st.number_input("Proposed spend (£)", 0.0, 1_000_000.0, 5_000.0, 100.0)
        new_quality = st.number_input("Proposed quality", 1.0, 10.0, 8.0, 0.1)

    if st.button("Compare scenarios", use_container_width=True):
        baseline = {
            "Followers": base_followers,
            "EngagementRate (%)": base_engagement,
            "AdSpend (GBP)": base_spend,
            "ContentQuality": base_quality,
        }
        proposed = {
            "Followers": new_followers,
            "EngagementRate (%)": new_engagement,
            "AdSpend (GBP)": new_spend,
            "ContentQuality": new_quality,
        }
        comparison = compare_scenarios(bundle, baseline, proposed)
        x, y, z = st.columns(3)
        x.metric("Baseline forecast", f"{comparison['baseline_sales']:,}")
        y.metric("Proposed forecast", f"{comparison['proposed_sales']:,}")
        z.metric("Expected uplift", f"{comparison['expected_uplift_units']:+,}")
        if comparison["incremental_cost_per_sale_gbp"] is not None:
            st.metric(
                "Incremental cost per predicted sale",
                f"£{comparison['incremental_cost_per_sale_gbp']:.2f}",
            )
        st.caption("Scenario changes are predictive associations, not causal guarantees.")

with model_tab:
    st.markdown("### Original case-study benchmark")
    benchmark = pd.DataFrame(
        [
            {"Model": "Tuned Ridge (selected)", "RMSE": 2000.36, "MAE": 1592.73, "R²": 0.4925},
            {"Model": "Linear Regression", "RMSE": 2000.36, "MAE": 1592.73, "R²": 0.4925},
            {"Model": "Tuned XGBoost", "RMSE": 2016.98, "MAE": 1609.08, "R²": 0.4840},
        ]
    )
    st.dataframe(benchmark, hide_index=True, use_container_width=True)

    st.markdown("### Loaded public demo model")
    demo_metrics = bundle.metrics
    first, second, third, fourth = st.columns(4)
    first.metric("Version", bundle.model_version)
    second.metric("Cross-validated RMSE", f"{demo_metrics.get('rmse', 0):,.0f}")
    third.metric("Cross-validated MAE", f"{demo_metrics.get('mae', 0):,.0f}")
    fourth.metric("Cross-validated R²", f"{demo_metrics.get('r2', 0):.3f}")

    st.info(
        "These demo metrics come from synthetic data generated at first run. They verify the "
        "end-to-end application but are not substitutes for the original case-study benchmark."
    )

    ranges = pd.DataFrame(bundle.training_ranges).T.reset_index(names="Feature")
    st.markdown("#### Demo-model training ranges")
    st.dataframe(ranges, hide_index=True, use_container_width=True)

    with st.expander("View technical model metadata"):
        st.json(
            {
                "version": bundle.model_version,
                "alpha": bundle.alpha,
                "metrics": bundle.metrics,
                "training_ranges": bundle.training_ranges,
            }
        )

    st.markdown(
        "See [`MODEL_CARD.md`](https://github.com/mohit231007/influencelift-ai/blob/main/"
        "MODEL_CARD.md) for intended use, limitations, validation results, and monitoring guidance."
    )

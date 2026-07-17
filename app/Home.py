"""Streamlit application for campaign forecasting and scenario analysis."""

from __future__ import annotations

import pandas as pd
import streamlit as st

from influencelift.cleaning import audit_campaign_data
from influencelift.inference import load_or_create_bundle, predict_campaigns
from influencelift.simulation import compare_scenarios

st.set_page_config(page_title="InfluenceLift AI", page_icon="📈", layout="wide")


@st.cache_resource
def model_bundle():
    return load_or_create_bundle()


bundle = model_bundle()

st.title("InfluenceLift AI")
st.subheader("Predict influencer campaign sales before the budget is spent.")
st.caption(
    "A production-style demonstration of messy-data cleaning, regression, uncertainty, "
    "and marketing scenario analysis."
)

metric_columns = st.columns(4)
metric_columns[0].metric("Model", "Ridge")
metric_columns[1].metric("Case-study RMSE", "2,000")
metric_columns[2].metric("Case-study R²", "0.493")
metric_columns[3].metric("Loaded version", bundle.model_version)

predictor_tab, batch_tab, simulator_tab, model_tab = st.tabs(
    ["Campaign predictor", "Batch predictions", "Scenario simulator", "Model information"]
)

with predictor_tab:
    st.markdown("### Forecast a single campaign")
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
        b.metric("Lower interval", f"{prediction['Prediction_Lower_95']:,}")
        c.metric("Upper interval", f"{prediction['Prediction_Upper_95']:,}")
        st.info(f"Data-quality status: **{report.status}**")
        if prediction["Corrections_Applied"]:
            st.write("Corrections:", prediction["Corrections_Applied"])
        if prediction["Extrapolation_Warnings"]:
            st.warning(f"Extrapolation warning: {prediction['Extrapolation_Warnings']}")

with batch_tab:
    st.markdown("### Upload campaign data")
    uploaded = st.file_uploader("CSV file", type=["csv"])
    if uploaded is None:
        st.code(
            "Followers,EngagementRate (%),AdSpend (GBP),ContentQuality,ID\n"
            "125K,3.7%,£5500,8.2,1"
        )
    else:
        uploaded_frame = pd.read_csv(uploaded)
        st.dataframe(uploaded_frame.head(20), use_container_width=True)
        try:
            report = audit_campaign_data(uploaded_frame)
            st.json(report.to_dict())
            predictions = predict_campaigns(bundle, uploaded_frame)
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
    st.markdown("### Loaded model")
    st.json(
        {
            "version": bundle.model_version,
            "alpha": bundle.alpha,
            "metrics": bundle.metrics,
            "training_ranges": bundle.training_ranges,
        }
    )
    st.markdown(
        "See `MODEL_CARD.md` for intended use, limitations, validation results, and monitoring guidance."
    )

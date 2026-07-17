"""Scenario-comparison helpers for marketing decision support."""

from __future__ import annotations

from typing import Any

import pandas as pd

from influencelift.inference import ModelBundle, predict_campaigns


def compare_scenarios(
    bundle: ModelBundle,
    baseline: dict[str, Any],
    proposed: dict[str, Any],
) -> dict[str, Any]:
    frame = pd.DataFrame([baseline, proposed])
    predictions = predict_campaigns(bundle, frame)
    baseline_sales = int(predictions.loc[0, "Predicted_Sales_Units"])
    proposed_sales = int(predictions.loc[1, "Predicted_Sales_Units"])
    uplift = proposed_sales - baseline_sales

    baseline_spend = float(str(baseline["AdSpend (GBP)"]).replace("£", "").replace(",", ""))
    proposed_spend = float(str(proposed["AdSpend (GBP)"]).replace("£", "").replace(",", ""))
    incremental_spend = proposed_spend - baseline_spend
    incremental_cost_per_sale = None
    if uplift > 0 and incremental_spend > 0:
        incremental_cost_per_sale = incremental_spend / uplift

    return {
        "baseline_sales": baseline_sales,
        "proposed_sales": proposed_sales,
        "expected_uplift_units": uplift,
        "incremental_spend_gbp": incremental_spend,
        "incremental_cost_per_sale_gbp": incremental_cost_per_sale,
    }

# Model Card: InfluenceLift Ridge Baseline

## Model details

- **Task:** Regression
- **Target:** Campaign-attributed product sales in units
- **Selected estimator:** Ridge regression
- **Default regularisation:** `alpha=1.0`
- **Input variables:** Followers, engagement rate, ad spend, and content quality
- **Output:** Non-negative predicted sales units with an empirical residual interval

## Intended use

The model is intended to support pre-campaign planning, scenario comparison, data-quality checks, and marketing analytics demonstrations.

It should be used as one input into a decision process, alongside product margin, creator-brand fit, audience demographics, inventory, historical incrementality, and campaign objectives.

## Out-of-scope use

Do not use the model to:

- Make automatic employment or creator-contract decisions without human review.
- Claim causal sales lift from observational associations.
- Forecast campaigns whose channels, geography, product category, or scale materially differ from the training population without validation.
- Process personal or sensitive creator data that is not needed for the prediction task.

## Validation result

Five-fold out-of-fold validation on the original case-study training data produced:

| Metric | Result |
|---|---:|
| RMSE | 2,000.36 units |
| MAE | 1,592.73 units |
| R² | 0.4925 |
| RMSE fold standard deviation | 44.57 units |

The tuned Ridge model slightly outperformed a tuned XGBoost benchmark. This supports selecting the simpler model for interpretability and operational reliability.

## Data preparation

The pipeline handles:

- Currency symbols and comma separators.
- Percentage symbols.
- `K` and `M` suffixes.
- Missing values through median imputation.
- Negative engagement or spend values as likely sign errors, under the default policy.
- Dataset-specific follower and spend scale anomalies.
- Content-quality values outside the configured range as invalid and missing.

All heuristic repairs are recorded by the audit layer and can be disabled or changed through `CleaningPolicy`.

## Limitations

- Campaign sales attribution may itself be noisy.
- The available features omit product price, category, creator-audience fit, posting frequency, channel, creative format, seasonality, and organic baseline sales.
- Prediction intervals are empirical residual bands, not formal conditional coverage guarantees.
- Observational coefficients must not be presented as causal effects.
- Dataset-specific scale repairs may be inappropriate for other organisations; validate policy thresholds before deployment.

## Monitoring recommendations

Monitor:

- Input missingness and correction rates.
- Feature distributions and out-of-range frequency.
- Residual RMSE and MAE when actual sales become available.
- Prediction interval coverage.
- Performance by product category, creator segment, and campaign period.
- Frequency of extrapolation outside training ranges.

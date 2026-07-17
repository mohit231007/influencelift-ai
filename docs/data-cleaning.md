# Data-cleaning design

The cleaning layer has two outputs:

1. A numeric model matrix.
2. An audit trail describing every correction or invalid value.

## Supported formats

- Currency: `£5,000`, `$5000`, `€5000`, `₹5000`
- Percentages: `3.2%`
- Scaled counts: `125K`, `1.4M`, `0.2B`
- Missing markers: empty strings, `None`, `null`, `N/A`, and `-`

## Dataset-specific policies

The case-study data contains two systematic scale anomalies:

- Follower values below 1,000 represent thousands.
- Extreme follower and spend values are inflated by fixed factors.

These rules are configurable through `CleaningPolicy`. They must be reassessed before applying the project to a different organisation's data.

## Invalid values

- Negative followers are invalid.
- Engagement above 100% is invalid.
- Content-quality scores outside 1–10 are invalid.
- Invalid values become missing and are imputed inside the model pipeline.

Negative engagement and spend are interpreted as sign errors under the default policy and converted to absolute values. The audit report always records the correction.

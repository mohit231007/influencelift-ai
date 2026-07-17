# Deployment guide

This guide covers local Windows QA, Streamlit Community Cloud deployment, and an optional FastAPI deployment.

## Local QA on Windows PowerShell

From a normal PowerShell window:

```powershell
git clone https://github.com/mohit231007/influencelift-ai.git
cd influencelift-ai
git checkout agent/deployment-readiness
Set-ExecutionPolicy -Scope Process Bypass
.\scripts\qa_local.ps1 -LaunchApp -LaunchApi
```

The script will:

1. Prefer Python 3.12, then 3.11 or 3.10.
2. Create `.venv` if required.
3. Install the project and development dependencies.
4. Run Ruff, Pytest, and module compilation.
5. Generate deterministic synthetic data.
6. Train a three-fold QA model.
7. Generate batch predictions.
8. Optionally launch Streamlit and FastAPI.

Expected local URLs:

- Streamlit: <http://localhost:8501>
- FastAPI documentation: <http://localhost:8000/docs>
- FastAPI health: <http://localhost:8000/health>

For repeat checks after the first installation:

```powershell
.\scripts\qa_local.ps1 -SkipInstall -LaunchApp -LaunchApi
```

## Manual acceptance checklist

### Campaign predictor

- Enter `125K` followers.
- Enter `3.7%` engagement.
- Enter `£5,500` ad spend.
- Set content quality to `8.2`.
- Confirm a non-negative forecast and prediction interval are displayed.
- Confirm currency, percentage, and explicit-scale corrections are reported.

### Batch predictions

- Upload `data/sample/synthetic_campaigns.csv`.
- Confirm a data-quality report appears.
- Confirm predictions are generated for every row.
- Download `influencelift_predictions.csv` and open it successfully.

### Scenario simulator

- Compare the default baseline and proposed campaign.
- Confirm baseline sales, proposed sales, expected uplift, and incremental cost per predicted sale are displayed.

### API

Open <http://localhost:8000/docs> and execute `POST /predict` with:

```json
{
  "followers": "125K",
  "engagement_rate": "3.7%",
  "ad_spend": "£5,500",
  "content_quality": 8.2,
  "timestamp": "2026-07-17"
}
```

Confirm the response includes:

- `predicted_sales_units`
- `prediction_lower_bound`
- `prediction_upper_bound`
- `data_quality_status`
- `corrections_applied`
- `model_version`

## Streamlit Community Cloud

Create an application from the public GitHub repository using:

```text
Repository: mohit231007/influencelift-ai
Branch: main
Main file: app/Home.py
Python: 3.12
```

No secrets are required for the demonstration application. The app creates a deterministic synthetic demo model when no model artifact exists.

After deployment, run the same manual acceptance checklist against the public URL.

## FastAPI deployment

The API can be deployed to a Python-compatible container or web-service platform.

Recommended start command:

```bash
uvicorn api.main:app --host 0.0.0.0 --port $PORT
```

Recommended health check:

```text
/health
```

The repository also supports Docker:

```bash
docker compose up --build
```

## Operational notes

- The model estimates predictive associations rather than causal effects.
- The public sample dataset is synthetic.
- The original challenge data must remain outside Git unless redistribution rights are confirmed.
- Free hosting tiers may sleep during inactivity and can have a slower first request.

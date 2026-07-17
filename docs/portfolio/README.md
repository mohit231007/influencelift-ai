# InfluenceLift AI Portfolio Defense Bundle

This directory turns the working ML product into a structured interview, system-design, coding, and career-marketing portfolio.

## Bundle contents

| Guide | Length | Purpose |
|---|---:|---|
| System Design Portfolio Defense Guide | 42 pages | Architecture, requirements, data flow, model lifecycle, deployment, security, monitoring, scale, trade-offs, and project defense |
| Coding Guide | 42 pages | Repository walkthrough, parser and cleaning logic, scikit-learn pipeline, evaluation, inference, API, Streamlit, tests, CI, Docker, and extension patterns |
| Coding Interview Workbook | 42 pages | Forty project-grounded implementation, debugging, API, testing, MLOps, and system exercises |
| Interview Question Bank | 42 pages | Two hundred questions with concise model answers across business, ML, Python, APIs, MLOps, system design, and behavioural interviews |
| Portfolio Playbook | 42 pages | README, GitHub, resume, LinkedIn, recruiter journey, STAR stories, demo scripts, outreach, and a 90-day promotion plan |
| System Design Diagram Pack | 42 pages | Twenty diagrams and twenty matching defense sheets for whiteboard interviews |
| LinkedIn Marketing Kit | 18 pages | Launch posts, carousel copy, project-section text, recruiter messages, replies, hashtags, and content schedule |

The complete editable DOCX and PDF editions are maintained as the **InfluenceLift AI Portfolio Defense Bundle**. The repository includes the two most reusable public source assets:

- [LinkedIn Marketing Kit](LinkedIn_Marketing_Kit.md)
- [System Design Diagrams](System_Design_Diagrams.md)

## Recommended study order

1. Run the [live application](https://influencelift-ai.streamlit.app) and rehearse the single, batch, and scenario flows.
2. Review the system-design guide and draw the context, container, request-flow, training, deployment, and scale-out diagrams.
3. Use the coding guide while opening the matching package, API, app, test, and workflow files.
4. Complete the workbook without reading the reference answer first.
5. Practise five question-bank pages per day and add a repository evidence reference to every answer.
6. Use the portfolio playbook and LinkedIn kit to publish and promote the project without overclaiming.

## Project ownership and collaboration

- **Mohit Bhatnagar:** data science, data cleaning, modelling, ML engineering, FastAPI, Streamlit, testing, Docker, CI/CD, deployment, documentation, and open-source packaging.
- **Aarushi Rai:** marketing-use-case framing and portfolio positioning.

The project should be described as a collaboration with explicit role attribution rather than assigning all technical implementation or all business framing to one person.

## Core interview proof points

- The original case-study model was selected through five-fold cross-validation.
- Tuned Ridge achieved approximately **2,000 RMSE**, **1,593 MAE**, and **0.493 R²**.
- A tuned XGBoost challenger was slightly worse, supporting the simpler production baseline.
- Cleaning, imputation, scaling, and inference share one pipeline to prevent training-serving skew.
- Predictions include empirical bounds, correction metadata, extrapolation warnings, and model version.
- The system provides Streamlit, FastAPI, CLI, Docker, automated tests, multi-version CI, deployment smoke tests, and a public synthetic-data demo.
- The original challenge data is not redistributed.
- Scenario outputs are predictive associations, not causal guarantees.

## Two-minute defense structure

1. **Problem:** marketing teams must estimate sales before committing campaign budget, but source data is inconsistent.
2. **Solution:** auditable cleaning plus a leakage-safe regression pipeline and decision-oriented interfaces.
3. **Model decision:** Ridge was selected because it delivered the strongest combination of validation accuracy, stability, explainability, and operating simplicity.
4. **Product:** single prediction, batch audit and download, scenario comparison, API access, and model information.
5. **Engineering:** reusable package, tests, CI, smoke tests, Docker, model card, and public deployment.
6. **Limitations:** observational attribution, a limited feature set, a simple residual interval, and a synthetic hosted model.
7. **Next step:** per-prediction explanations and persisted outcome monitoring before adding model complexity.

## Interview ground rule

Never imply that the synthetic public-demo model produced the original case-study metrics. Always distinguish:

- **Original case-study validation:** supplied challenge data and the reported benchmark metrics.
- **Public live demo:** deterministic synthetic training data used to make the repository safely runnable.

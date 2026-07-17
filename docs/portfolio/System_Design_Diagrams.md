# System Design Diagram Pack

> Twenty whiteboard-ready diagrams plus defense notes for architecture, data, ML, deployment, security, scale, and operations.

**Author:** Mohit Bhatnagar  
**Collaboration:** Aarushi Rai - marketing analytics framing and portfolio positioning  
**Live app:** https://influencelift-ai.streamlit.app  
**Repository:** https://github.com/mohit231007/influencelift-ai

## 01. System Context

```mermaid
flowchart LR
    N0["Marketing manager"]
    N1["InfluenceLift AI"]
    N2["Recruiter / reviewer"]
    N3["GitHub"]
    N4["Streamlit Cloud"]
    N0 --> N1
    N2 --> N1
    N1 --> N3
    N3 --> N4
```

## 02. Container Architecture

```mermaid
flowchart LR
    N0["Streamlit UI"]
    N1["FastAPI API"]
    N2["influencelift package"]
    N3["Model bundle"]
    N4["GitHub Actions"]
    N0 --> N2
    N1 --> N2
    N2 --> N3
    N4 --> N0
    N4 --> N1
```

## 03. Single Prediction Flow

```mermaid
flowchart LR
    N0["User input"]
    N1["Schema validation"]
    N2["CampaignCleaner"]
    N3["Imputer + scaler"]
    N4["Ridge model"]
    N5["Prediction + interval"]
    N6["UI response"]
    N0 --> N1
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
    N5 --> N6
```

## 04. Batch Prediction Flow

```mermaid
flowchart LR
    N0["CSV upload"]
    N1["Preview"]
    N2["Batch audit"]
    N3["Shared pipeline"]
    N4["Prediction table"]
    N5["CSV download"]
    N0 --> N1
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
```

## 05. Data Quality Pipeline

```mermaid
flowchart LR
    N0["Raw strings"]
    N1["Parser"]
    N2["Repair policy"]
    N3["Invalid masking"]
    N4["Audit flags"]
    N5["Clean features"]
    N0 --> N1
    N1 --> N2
    N2 --> N3
    N3 --> N5
    N2 --> N4
    N4 --> N5
```

## 06. Training Pipeline

```mermaid
flowchart LR
    N0["Training CSV"]
    N1["Fold split"]
    N2["Cleaner"]
    N3["Imputer"]
    N4["Scaler"]
    N5["Ridge"]
    N6["OOF metrics"]
    N7["Final bundle"]
    N0 --> N1
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
    N5 --> N6
    N6 --> N7
```

## 07. Model Selection Loop

```mermaid
flowchart LR
    N0["Baseline"]
    N1["Linear"]
    N2["Ridge grid"]
    N3["Tree challenger"]
    N4["Cross-validation"]
    N5["Metric comparison"]
    N6["Selected model"]
    N0 --> N4
    N1 --> N4
    N2 --> N4
    N3 --> N4
    N4 --> N5
    N5 --> N6
```

## 08. Prediction Uncertainty

```mermaid
flowchart LR
    N0["OOF predictions"]
    N1["Residuals"]
    N2["95% absolute quantile"]
    N3["Point prediction"]
    N4["Lower bound"]
    N5["Upper bound"]
    N0 --> N1
    N1 --> N2
    N2 --> N4
    N2 --> N5
    N3 --> N4
    N3 --> N5
```

## 09. API Request Sequence

```mermaid
flowchart LR
    N0["Client"]
    N1["FastAPI"]
    N2["Pydantic"]
    N3["Inference package"]
    N4["Model bundle"]
    N5["Response schema"]
    N0 --> N1
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N3
    N3 --> N5
    N5 --> N0
```

## 10. Scenario Simulation

```mermaid
flowchart LR
    N0["Baseline inputs"]
    N1["Proposed inputs"]
    N2["Shared model"]
    N3["Baseline forecast"]
    N4["Proposed forecast"]
    N5["Uplift + cost/sale"]
    N0 --> N2
    N1 --> N2
    N2 --> N3
    N2 --> N4
    N3 --> N5
    N4 --> N5
```

## 11. Deployment Topology

```mermaid
flowchart LR
    N0["Browser"]
    N1["Streamlit Cloud"]
    N2["GitHub main"]
    N3["Synthetic data"]
    N4["Demo bundle"]
    N5["Optional local API"]
    N0 --> N1
    N2 --> N1
    N3 --> N1
    N1 --> N4
    N0 --> N5
```

## 12. CI/CD Pipeline

```mermaid
flowchart LR
    N0["Feature branch"]
    N1["Pull request"]
    N2["Install"]
    N3["Lint"]
    N4["Tests"]
    N5["Compile"]
    N6["Smoke services"]
    N7["Merge main"]
    N8["Redeploy"]
    N0 --> N1
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
    N5 --> N6
    N6 --> N7
    N7 --> N8
```

## 13. Observability Model

```mermaid
flowchart LR
    N0["Prediction request"]
    N1["Structured log"]
    N2["Metric counters"]
    N3["Prediction ledger"]
    N4["Actual sales"]
    N5["Performance dashboard"]
    N6["Alert"]
    N0 --> N1
    N0 --> N2
    N0 --> N3
    N4 --> N3
    N3 --> N5
    N2 --> N5
    N5 --> N6
```

## 14. Security Boundaries

```mermaid
flowchart LR
    N0["Public browser"]
    N1["Streamlit app"]
    N2["Input validator"]
    N3["Model package"]
    N4["No secret zone"]
    N5["Future auth gateway"]
    N0 --> N1
    N1 --> N2
    N2 --> N3
    N4 --> N1
    N5 --> N1
```

## 15. Threat Model

```mermaid
flowchart LR
    N0["Oversized upload"]
    N1["Malformed payload"]
    N2["Untrusted artefact"]
    N3["Dependency risk"]
    N4["Rate abuse"]
    N5["Controls"]
    N0 --> N5
    N1 --> N5
    N2 --> N5
    N3 --> N5
    N4 --> N5
```

## 16. Scale-out Architecture

```mermaid
flowchart LR
    N0["API gateway"]
    N1["Interactive API"]
    N2["Object storage"]
    N3["Job queue"]
    N4["Batch workers"]
    N5["Prediction DB"]
    N6["Monitoring"]
    N0 --> N1
    N0 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
    N1 --> N5
    N1 --> N6
    N4 --> N6
```

## 17. Model Lifecycle

```mermaid
flowchart LR
    N0["Data profile"]
    N1["Train"]
    N2["Validate"]
    N3["Approve"]
    N4["Register"]
    N5["Deploy"]
    N6["Monitor"]
    N7["Retrain decision"]
    N0 --> N1
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N4 --> N5
    N5 --> N6
    N6 --> N7
    N7 --> N0
```

## 18. Failure Handling

```mermaid
flowchart LR
    N0["Input failure"]
    N1["Model load failure"]
    N2["Inference failure"]
    N3["Batch timeout"]
    N4["Error mapper"]
    N5["User-safe response"]
    N6["Alert / retry"]
    N0 --> N4
    N1 --> N4
    N2 --> N4
    N3 --> N4
    N4 --> N5
    N4 --> N6
```

## 19. Data Storage Future

```mermaid
flowchart LR
    N0["Raw object store"]
    N1["Campaign table"]
    N2["Prediction run"]
    N3["Prediction rows"]
    N4["Outcome table"]
    N5["Model registry"]
    N6["Analytics mart"]
    N0 --> N1
    N1 --> N2
    N2 --> N3
    N3 --> N4
    N5 --> N2
    N2 --> N6
    N4 --> N6
```

## 20. Roadmap Evolution

```mermaid
flowchart LR
    N0["v1 public demo"]
    N1["v1.1 explainability"]
    N2["v1.2 monitoring"]
    N3["v2 optimisation"]
    N4["Enterprise governance"]
    N0 --> N1
    N1 --> N2
    N2 --> N3
    N3 --> N4
```

## Diagram defense method

For every diagram, explain five things in order:

1. **Responsibility** - what each box owns.
2. **Boundary** - where data, trust, deployment, or team ownership changes.
3. **Evidence** - which code, test, metric, or live workflow proves it exists.
4. **Failure mode** - what breaks and how the user receives a safe response.
5. **Evolution** - the first architecture change required at 100x scale.

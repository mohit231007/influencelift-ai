# Architecture

InfluenceLift AI separates interface code from reusable domain logic.

```mermaid
flowchart TB
    subgraph Interfaces
      S[Streamlit]
      A[FastAPI]
      C[CLI scripts]
    end
    subgraph Domain package
      V[Schema validation]
      Q[Data-quality audit]
      T[CampaignCleaner]
      M[Model pipeline]
      U[Uncertainty and range checks]
      X[Scenario comparison]
    end
    subgraph Persistence
      B[Joblib model bundle]
      D[Local CSV data]
    end

    S --> Q
    S --> M
    S --> X
    A --> V
    A --> M
    C --> M
    D --> T
    T --> M
    M --> B
    B --> U
```

## Design decisions

- Cleaning is implemented as a scikit-learn transformer so training and inference cannot drift apart.
- The saved artifact is a model bundle containing the pipeline, validation metrics, residual interval, model version, and training ranges.
- Interfaces use the package API instead of duplicating transformations.
- The application creates a deterministic synthetic demo model when no local artifact exists, which makes the repository runnable after installation.
- Original datasets stay outside version control unless redistribution rights are confirmed.

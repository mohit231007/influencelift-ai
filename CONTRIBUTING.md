# Contributing

Thank you for considering a contribution to InfluenceLift AI.

## Development workflow

1. Fork the repository and create a focused feature branch.
2. Install the development dependencies with `pip install -e ".[dev]"`.
3. Add or update tests for every behaviour change.
4. Run `ruff check .` and `pytest -q`.
5. Open a pull request that explains the business and technical impact.

## Design principles

- Prefer explicit, testable cleaning rules over hidden heuristics.
- Keep training and inference transformations identical.
- Do not add proprietary or personally identifiable campaign data.
- Treat model outputs as decision support, not causal proof.
- Document new assumptions in the model card.

## Commit style

Use concise imperative messages, for example:

- `Add batch prediction endpoint`
- `Harden currency parser`
- `Document model limitations`

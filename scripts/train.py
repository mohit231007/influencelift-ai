#!/usr/bin/env python
"""Train and evaluate an InfluenceLift model bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from influencelift.modeling import save_bundle, train_bundle


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--model-output", default="artifacts/model_bundle.joblib")
    parser.add_argument("--metrics-output", default="artifacts/metrics.json")
    parser.add_argument("--alpha", type=float, default=1.0)
    parser.add_argument("--folds", type=int, default=5)
    parser.add_argument("--model-version", default="1.0.0")
    args = parser.parse_args()

    frame = pd.read_csv(args.input)
    bundle = train_bundle(
        frame,
        alpha=args.alpha,
        folds=args.folds,
        model_version=args.model_version,
    )
    save_bundle(bundle, args.model_output)

    metrics_path = Path(args.metrics_output)
    metrics_path.parent.mkdir(parents=True, exist_ok=True)
    metrics_path.write_text(json.dumps(bundle["metrics"], indent=2), encoding="utf-8")

    print(json.dumps(bundle["metrics"], indent=2))
    print(f"Model saved to {args.model_output}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python
"""Generate batch predictions from a trained model bundle."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from influencelift.inference import load_bundle, predict_campaigns


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--model", default="artifacts/model_bundle.joblib")
    parser.add_argument("--output", default="artifacts/predictions.csv")
    args = parser.parse_args()

    frame = pd.read_csv(args.input)
    bundle = load_bundle(args.model)
    predictions = predict_campaigns(bundle, frame)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(output, index=False)
    print(f"Wrote {len(predictions):,} predictions to {output}")


if __name__ == "__main__":
    main()

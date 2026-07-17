#!/usr/bin/env python
"""Generate a synthetic campaign dataset that is safe to publish."""

from __future__ import annotations

import argparse
from pathlib import Path

from influencelift.demo_data import generate_demo_dataset


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rows", type=int, default=1500)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="data/generated/demo_train.csv")
    args = parser.parse_args()

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    frame = generate_demo_dataset(rows=args.rows, seed=args.seed, messy=True)
    frame.to_csv(output, index=False)
    print(f"Wrote {len(frame):,} rows to {output}")


if __name__ == "__main__":
    main()

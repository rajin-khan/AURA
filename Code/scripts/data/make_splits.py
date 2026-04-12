from __future__ import annotations

import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from aura.data_engine.manifest import load_pair_manifest_jsonl, write_pair_manifest_jsonl
from aura.data_engine.splits import assign_random_splits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="Input manifest JSONL")
    ap.add_argument("--out", required=True, help="Output manifest JSONL with assigned splits")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--train-ratio", type=float, default=0.7)
    ap.add_argument("--val-ratio", type=float, default=0.15)
    ap.add_argument("--test-ratio", type=float, default=0.15)
    ap.add_argument("--stratify-by", default="label")
    args = ap.parse_args()

    samples = load_pair_manifest_jsonl(args.manifest)
    assigned = assign_random_splits(
        samples,
        train_ratio=args.train_ratio,
        val_ratio=args.val_ratio,
        test_ratio=args.test_ratio,
        seed=args.seed,
        stratify_by=args.stratify_by,
    )
    write_pair_manifest_jsonl(args.out, assigned)
    print(f"wrote {len(assigned)} samples -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

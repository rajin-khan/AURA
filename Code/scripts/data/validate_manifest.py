from __future__ import annotations

import argparse
import os
import sys

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from aura.data_engine.manifest import load_pair_manifest_jsonl
from aura.data_engine.validate import validate_samples


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="Path to pair manifest JSONL")
    args = ap.parse_args()

    samples = load_pair_manifest_jsonl(args.manifest)
    report = validate_samples(samples, manifest_path=args.manifest)

    print(report.summary())
    for issue in report.errors:
        print(f"ERROR [{issue.sample_id}] {issue.message}")
    for issue in report.warnings:
        print(f"WARN  [{issue.sample_id}] {issue.message}")

    return 0 if report.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())

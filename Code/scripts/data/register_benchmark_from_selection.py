from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from aura.data_engine.benchmark_manifest import write_benchmark_manifest_jsonl
from aura.data_engine.benchmark_schema import BenchmarkSample


GENERATORS = {
    "adm",
    "biggan",
    "glide",
    "midjourney",
    "stable_diffusion_v1_4",
    "stable_diffusion_v1_5",
    "vqdm",
    "wukong",
}


def infer_metadata(path: Path) -> tuple[str, str | None, str | None]:
    parts = list(path.parts)
    lower = [p.lower() for p in parts]

    if "real" in lower:
        class_name = parts[-2] if len(parts) >= 2 else None
        return "real", None, class_name

    if "synthetic" in lower:
        generator = None
        for p in lower:
            if p in GENERATORS:
                generator = p
                break
        class_name = parts[-2] if len(parts) >= 2 else None
        return "synthetic", generator, class_name

    return "unknown", None, None


def load_selection_file(path: Path) -> list[Path]:
    if not path.exists():
        return []
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines()]
    return [Path(line) for line in lines if line]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--selection-dir", required=True, help="Directory with selected_*.txt files")
    ap.add_argument("--dataset-name", required=True)
    ap.add_argument("--out", required=True, help="Output benchmark manifest JSONL")
    args = ap.parse_args()

    selection_dir = Path(args.selection_dir).resolve()
    paths: list[Path] = []
    for file in sorted(selection_dir.glob("selected*.txt")):
        paths.extend(load_selection_file(file))

    samples: list[BenchmarkSample] = []
    for path in sorted(paths):
        label, generator, class_name = infer_metadata(path)
        sample_id = str(path).replace(os.sep, "__")
        samples.append(
            BenchmarkSample(
                id=sample_id,
                dataset=args.dataset_name,
                split="unspecified",
                image_path=str(path),
                label=label,
                generator=generator,
                class_name=class_name,
                source_type="public-benchmark",
                domain="natural-image",
                notes="registered from deterministic selection list",
            )
        )

    write_benchmark_manifest_jsonl(args.out, samples)
    print(f"registered {len(samples)} selected benchmark samples -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

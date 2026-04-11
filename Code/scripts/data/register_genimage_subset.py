from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "..", "src"))

from aura.data_engine.benchmark_manifest import write_benchmark_manifest_jsonl
from aura.data_engine.benchmark_schema import BenchmarkSample


IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}


def detect_label_and_generator(path: Path) -> tuple[str, str | None]:
    parts = {p.lower() for p in path.parts}
    generator_names = [
        "adm",
        "biggan",
        "glide",
        "midjourney",
        "stable_diffusion_v1_4",
        "stable_diffusion_v1_5",
        "vqdm",
        "wukong",
    ]
    for g in generator_names:
        if g in parts:
            return "synthetic", g
    if "nature" in parts or "real" in parts:
        return "real", None
    return "unknown", None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Root directory of a local GenImage subset")
    ap.add_argument("--dataset-name", default="genimage-mini-v1")
    ap.add_argument("--out", required=True, help="Output benchmark manifest JSONL")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    samples: list[BenchmarkSample] = []

    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTS:
            continue
        label, generator = detect_label_and_generator(path)
        rel = path.relative_to(root)
        sample_id = str(rel).replace(os.sep, "__")
        class_name = rel.parts[-2] if len(rel.parts) >= 2 else None
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
                notes="registered from local GenImage subset",
            )
        )

    write_benchmark_manifest_jsonl(args.out, samples)
    print(f"registered {len(samples)} benchmark samples -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

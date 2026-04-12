from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from aura.data_engine.benchmark_schema import BenchmarkSample


OPTIONAL_DEFAULTS = {
    "split": "unspecified",
    "label": "unknown",
    "generator": None,
    "source_type": "public-benchmark",
    "domain": "natural-image",
    "class_name": None,
    "license": None,
    "notes": None,
}


def load_benchmark_manifest_jsonl(path: str | Path) -> List[BenchmarkSample]:
    p = Path(path)
    out: List[BenchmarkSample] = []
    with p.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            obj = json.loads(line)
            merged = {**OPTIONAL_DEFAULTS, **obj}
            try:
                out.append(BenchmarkSample(**merged))
            except TypeError as e:
                raise ValueError(f"Manifest line {i} has invalid fields: {e}") from e
    return out


def write_benchmark_manifest_jsonl(path: str | Path, samples: Iterable[BenchmarkSample]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for sample in samples:
            f.write(json.dumps(sample.to_dict(), ensure_ascii=False) + "\n")

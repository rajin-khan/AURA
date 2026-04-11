from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal, Optional


BenchmarkLabel = Literal["real", "synthetic", "unknown"]
BenchmarkSplit = Literal["train", "val", "test", "unspecified"]


@dataclass(frozen=True)
class BenchmarkSample:
    id: str
    dataset: str
    split: BenchmarkSplit
    image_path: str
    label: BenchmarkLabel
    generator: Optional[str] = None
    source_type: str = "public-benchmark"
    domain: str = "natural-image"
    class_name: Optional[str] = None
    license: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


ALLOWED_BENCHMARK_LABELS = {"real", "synthetic", "unknown"}
ALLOWED_BENCHMARK_SPLITS = {"train", "val", "test", "unspecified"}

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Literal, Optional


Label = Literal["cosmetic", "ai", "mixed", "unknown"]
Split = Literal["train", "val", "test", "unspecified"]
SourceType = Literal[
    "internal-controlled",
    "public-benchmark",
    "public-derived",
    "synthetic-generated",
    "unknown",
]


@dataclass(frozen=True)
class PairSample:
    id: str
    dataset: str
    split: Split
    domain: str
    source_type: SourceType
    original_path: str
    edited_path: str
    label: Label
    edit_family: str
    edit_tool: Optional[str] = None
    edit_intent: Optional[str] = None
    is_paired: bool = True
    stress_parent: Optional[str] = None
    license: Optional[str] = None
    notes: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)

    def resolved_original_path(self, manifest_path: str | Path) -> Path:
        return _resolve_path(manifest_path, self.original_path)

    def resolved_edited_path(self, manifest_path: str | Path) -> Path:
        return _resolve_path(manifest_path, self.edited_path)


REQUIRED_FIELDS = {
    "id",
    "dataset",
    "split",
    "domain",
    "source_type",
    "original_path",
    "edited_path",
    "label",
    "edit_family",
}

ALLOWED_LABELS = {"cosmetic", "ai", "mixed", "unknown"}
ALLOWED_SPLITS = {"train", "val", "test", "unspecified"}
ALLOWED_SOURCE_TYPES = {
    "internal-controlled",
    "public-benchmark",
    "public-derived",
    "synthetic-generated",
    "unknown",
}


def _resolve_path(manifest_path: str | Path, sample_path: str) -> Path:
    p = Path(sample_path)
    if p.is_absolute():
        return p
    return Path(manifest_path).resolve().parent / p

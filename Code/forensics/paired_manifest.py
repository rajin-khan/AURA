from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Literal, Optional


Label = Literal["cosmetic", "ai", "mixed", "unknown"]


@dataclass(frozen=True)
class PairRecord:
    """A single original→edited pair with a label."""

    id: str
    original_path: str
    edited_path: str
    label: Label
    notes: Optional[str] = None


def load_manifest_jsonl(path: str | Path) -> List[PairRecord]:
    p = Path(path)
    records: List[PairRecord] = []

    with p.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            obj = json.loads(line)
            try:
                records.append(
                    PairRecord(
                        id=str(obj["id"]),
                        original_path=str(obj["original_path"]),
                        edited_path=str(obj["edited_path"]),
                        label=obj.get("label", "unknown"),
                        notes=obj.get("notes"),
                    )
                )
            except KeyError as e:
                raise ValueError(f"Manifest line {i} missing field: {e}") from e

    return records

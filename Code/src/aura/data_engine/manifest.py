from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, List

from aura.data_engine.schema import PairSample


OPTIONAL_DEFAULTS = {
    "split": "unspecified",
    "domain": "unknown",
    "source_type": "unknown",
    "label": "unknown",
    "edit_family": "unknown",
    "edit_tool": None,
    "edit_intent": None,
    "is_paired": True,
    "stress_parent": None,
    "license": None,
    "notes": None,
}


def load_pair_manifest_jsonl(path: str | Path) -> List[PairSample]:
    p = Path(path)
    out: List[PairSample] = []

    with p.open("r", encoding="utf-8") as f:
        for i, line in enumerate(f, start=1):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            obj = json.loads(line)
            merged = {**OPTIONAL_DEFAULTS, **obj}
            try:
                out.append(PairSample(**merged))
            except TypeError as e:
                raise ValueError(f"Manifest line {i} has invalid fields: {e}") from e

    return out


def write_pair_manifest_jsonl(path: str | Path, samples: Iterable[PairSample]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("w", encoding="utf-8") as f:
        for sample in samples:
            f.write(json.dumps(sample.to_dict(), ensure_ascii=False) + "\n")

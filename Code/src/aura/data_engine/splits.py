from __future__ import annotations

from collections import defaultdict
from typing import Dict, Iterable, List

import numpy as np

from aura.data_engine.schema import PairSample


def assign_random_splits(
    samples: Iterable[PairSample],
    *,
    train_ratio: float = 0.7,
    val_ratio: float = 0.15,
    test_ratio: float = 0.15,
    seed: int = 42,
    stratify_by: str = "label",
) -> List[PairSample]:
    total = train_ratio + val_ratio + test_ratio
    if abs(total - 1.0) > 1e-6:
        raise ValueError("train_ratio + val_ratio + test_ratio must equal 1.0")

    samples = list(samples)
    rng = np.random.default_rng(seed)

    groups: Dict[str, List[PairSample]] = defaultdict(list)
    for s in samples:
        key = getattr(s, stratify_by)
        groups[str(key)].append(s)

    out: List[PairSample] = []
    for _, group in groups.items():
        idx = np.arange(len(group))
        rng.shuffle(idx)

        n = len(group)
        n_train = int(round(train_ratio * n))
        n_val = int(round(val_ratio * n))
        if n_train + n_val > n:
            n_val = max(0, n - n_train)
        n_test = n - n_train - n_val

        for pos, j in enumerate(idx):
            sample = group[int(j)]
            if pos < n_train:
                split = "train"
            elif pos < n_train + n_val:
                split = "val"
            else:
                split = "test"
            out.append(
                PairSample(
                    id=sample.id,
                    dataset=sample.dataset,
                    split=split,
                    domain=sample.domain,
                    source_type=sample.source_type,
                    original_path=sample.original_path,
                    edited_path=sample.edited_path,
                    label=sample.label,
                    edit_family=sample.edit_family,
                    edit_tool=sample.edit_tool,
                    edit_intent=sample.edit_intent,
                    is_paired=sample.is_paired,
                    stress_parent=sample.stress_parent,
                    license=sample.license,
                    notes=sample.notes,
                )
            )

    out.sort(key=lambda s: s.id)
    return out

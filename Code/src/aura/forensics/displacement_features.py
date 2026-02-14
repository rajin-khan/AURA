from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Tuple

import numpy as np


@dataclass
class DisplacementFeatures:
    """Feature bundle for an (original, edited) pair."""

    e_orig: np.ndarray
    e_edit: np.ndarray
    d: np.ndarray

    d_l2: float
    d_cos_wrt_orig: float
    d_cos_wrt_edit: float
    cos_orig_edit: float

    def to_dict(self) -> Dict:
        return {
            "d_l2": float(self.d_l2),
            "d_cos_wrt_orig": float(self.d_cos_wrt_orig),
            "d_cos_wrt_edit": float(self.d_cos_wrt_edit),
            "cos_orig_edit": float(self.cos_orig_edit),
        }


def _safe_cos(a: np.ndarray, b: np.ndarray) -> float:
    denom = float(np.linalg.norm(a) * np.linalg.norm(b))
    if denom <= 1e-12:
        return 0.0
    return float(np.dot(a, b) / denom)


def compute_displacement_features(e_orig: np.ndarray, e_edit: np.ndarray) -> DisplacementFeatures:
    """Compute displacement vector + compact scalar features.

    Core definition (from Feb docs):

      d = E(edited) - E(original)
    """

    d = (e_edit - e_orig).astype(np.float32)

    d_l2 = float(np.linalg.norm(d))
    d_cos_wrt_orig = _safe_cos(d, e_orig)
    d_cos_wrt_edit = _safe_cos(d, e_edit)
    cos_orig_edit = _safe_cos(e_orig, e_edit)

    return DisplacementFeatures(
        e_orig=e_orig,
        e_edit=e_edit,
        d=d,
        d_l2=d_l2,
        d_cos_wrt_orig=d_cos_wrt_orig,
        d_cos_wrt_edit=d_cos_wrt_edit,
        cos_orig_edit=cos_orig_edit,
    )


def vectorize(d: DisplacementFeatures, *, include_raw: bool = False) -> Tuple[np.ndarray, Dict[str, int]]:
    """Turn features into an ML-ready vector.

    include_raw=True appends the raw displacement vector, which is useful for
    linear probes but increases dimensionality.
    """

    scalars = np.array(
        [
            d.d_l2,
            d.d_cos_wrt_orig,
            d.d_cos_wrt_edit,
            d.cos_orig_edit,
        ],
        dtype=np.float32,
    )

    idx = {"d_l2": 0, "d_cos_wrt_orig": 1, "d_cos_wrt_edit": 2, "cos_orig_edit": 3}

    if not include_raw:
        return scalars, idx

    vec = np.concatenate([scalars, d.d.astype(np.float32)], axis=0)
    return vec, idx

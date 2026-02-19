from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Iterable, Optional


class ValidationError(ValueError):
    pass


def _is_finite(x: float) -> bool:
    return not (math.isnan(x) or math.isinf(x))


def validate_probability(x: float, *, name: str) -> float:
    """Validate a probability-like scalar in [0,1].

    We *fail closed* (raise) by default because these values drive labeling.
    """

    xf = float(x)
    if not _is_finite(xf):
        raise ValidationError(f"{name} must be finite, got {x!r}")
    if xf < 0.0 or xf > 1.0:
        raise ValidationError(f"{name} must be in [0,1], got {xf}")
    return xf


def validate_weight(x: float, *, name: str) -> float:
    xf = float(x)
    if not _is_finite(xf):
        raise ValidationError(f"{name} must be finite, got {x!r}")
    if xf < 0.0:
        raise ValidationError(f"{name} must be >= 0, got {xf}")
    return xf


@dataclass(frozen=True)
class WeightCheck:
    total: float
    normalized: bool


def check_weights_sum_to_one(weights: Iterable[float], *, tol: float = 1e-6) -> WeightCheck:
    ws = [float(w) for w in weights]
    total = float(sum(ws))
    if not _is_finite(total):
        raise ValidationError("weights total must be finite")
    if total <= 0:
        raise ValidationError("weights total must be > 0")
    normalized = abs(total - 1.0) <= tol
    return WeightCheck(total=total, normalized=normalized)


def normalize_weights(*weights: float) -> tuple[float, ...]:
    chk = check_weights_sum_to_one(weights)
    if chk.normalized:
        return tuple(float(w) for w in weights)
    return tuple(float(w) / chk.total for w in weights)


def validate_optional_probability(x: Optional[float], *, name: str) -> Optional[float]:
    if x is None:
        return None
    return validate_probability(x, name=name)

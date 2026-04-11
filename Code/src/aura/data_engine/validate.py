from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from aura.data_engine.schema import (
    ALLOWED_LABELS,
    ALLOWED_SOURCE_TYPES,
    ALLOWED_SPLITS,
    PairSample,
)


@dataclass(frozen=True)
class ValidationIssue:
    level: str
    sample_id: str
    message: str


@dataclass(frozen=True)
class ValidationReport:
    ok: bool
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]

    def summary(self) -> str:
        return (
            f"ok={self.ok} errors={len(self.errors)} warnings={len(self.warnings)}"
        )


def validate_samples(samples: Iterable[PairSample], *, manifest_path: str | Path | None = None) -> ValidationReport:
    samples = list(samples)
    errors: List[ValidationIssue] = []
    warnings: List[ValidationIssue] = []

    id_counts = Counter(s.id for s in samples)
    for s in samples:
        if not s.id.strip():
            errors.append(ValidationIssue("error", s.id, "empty id"))
        if id_counts[s.id] > 1:
            errors.append(ValidationIssue("error", s.id, "duplicate id"))
        if s.label not in ALLOWED_LABELS:
            errors.append(ValidationIssue("error", s.id, f"invalid label: {s.label}"))
        if s.split not in ALLOWED_SPLITS:
            errors.append(ValidationIssue("error", s.id, f"invalid split: {s.split}"))
        if s.source_type not in ALLOWED_SOURCE_TYPES:
            errors.append(ValidationIssue("error", s.id, f"invalid source_type: {s.source_type}"))
        if not s.dataset.strip():
            errors.append(ValidationIssue("error", s.id, "empty dataset"))
        if not s.original_path.strip():
            errors.append(ValidationIssue("error", s.id, "empty original_path"))
        if not s.edited_path.strip():
            errors.append(ValidationIssue("error", s.id, "empty edited_path"))
        if s.original_path == s.edited_path:
            warnings.append(ValidationIssue("warning", s.id, "original_path equals edited_path"))
        if s.label == "unknown":
            warnings.append(ValidationIssue("warning", s.id, "label is unknown"))
        if s.edit_family == "unknown":
            warnings.append(ValidationIssue("warning", s.id, "edit_family is unknown"))

        if manifest_path is not None:
            original_exists = s.resolved_original_path(manifest_path).exists()
            edited_exists = s.resolved_edited_path(manifest_path).exists()
            if not original_exists:
                errors.append(ValidationIssue("error", s.id, f"missing original file: {s.original_path}"))
            if not edited_exists:
                errors.append(ValidationIssue("error", s.id, f"missing edited file: {s.edited_path}"))

    ok = len(errors) == 0
    return ValidationReport(ok=ok, errors=errors, warnings=warnings)

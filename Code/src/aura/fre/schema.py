from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Literal, Optional


RiskLabel = Literal["likely_authentic", "likely_synthetic", "inconclusive"]


@dataclass
class EvidenceItem:
    stream: Literal["provenance", "forensic", "semantic"]
    name: str
    weight: float
    score: float  # normalized 0..1 where higher = more risk
    note: Optional[str] = None

    def to_dict(self) -> Dict:
        return {
            "stream": self.stream,
            "name": self.name,
            "weight": float(self.weight),
            "score": float(self.score),
            "note": self.note,
        }


@dataclass
class RiskCard:
    label: RiskLabel
    risk_score: float
    confidence: float
    evidence: List[EvidenceItem]
    limitations: List[str]

    def to_dict(self) -> Dict:
        return {
            "label": self.label,
            "risk_score": float(self.risk_score),
            "confidence": float(self.confidence),
            "evidence": [e.to_dict() for e in self.evidence],
            "limitations": list(self.limitations),
        }

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from aura.fre.schema import EvidenceItem, RiskCard, RiskLabel


@dataclass
class FusionConfig:
    # Conservative defaults from `Aura-Forensic-Risk-Engine-v2.md`
    w_prov: float = 0.45
    w_forensic: float = 0.40
    w_sem: float = 0.15

    # Decision zones
    authentic_max: float = 0.10
    synthetic_min: float = 0.90


def fuse_evidence(
    *,
    p_prov_auth: float,
    p_forensic_synth: float,
    p_sem_anomaly: float,
    evidence: List[EvidenceItem],
    cfg: FusionConfig = FusionConfig(),
) -> Tuple[RiskCard, List[str]]:
    """Fuse evidence streams using the FRE-v2 scoring rule.

    risk_score = w1*(1 - P_prov_auth) + w2*P_forensic_synth + w3*P_sem_anomaly

    Returns a RiskCard plus a list of contradiction flags.
    """

    risk_score = (
        cfg.w_prov * (1.0 - float(p_prov_auth))
        + cfg.w_forensic * float(p_forensic_synth)
        + cfg.w_sem * float(p_sem_anomaly)
    )

    # Conservative: confidence is not just 1-risk_score.
    # For now we keep it simple and bounded.
    confidence = max(0.0, min(1.0, 1.0 - abs(risk_score - 0.5) * 2.0))

    if risk_score <= cfg.authentic_max:
        label: RiskLabel = "likely_authentic"
    elif risk_score >= cfg.synthetic_min:
        label = "likely_synthetic"
    else:
        label = "inconclusive"

    contradictions: List[str] = []
    # Example contradiction: strong provenance but strong forensic synth signal.
    if p_prov_auth >= 0.95 and p_forensic_synth >= 0.80:
        contradictions.append("contradiction: strong provenance + strong forensic synth signal")

    limitations = [
        "FRE-v2 is a scaffold; scores are only meaningful once calibrated on a benchmark.",
        "Semantic signal should not be used as the sole red-label trigger.",
    ]

    return (
        RiskCard(
            label=label,
            risk_score=float(risk_score),
            confidence=float(confidence),
            evidence=evidence,
            limitations=limitations,
        ),
        contradictions,
    )

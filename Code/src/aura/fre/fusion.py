from __future__ import annotations

from dataclasses import dataclass
from typing import List, Tuple

from aura.fre.schema import EvidenceItem, RiskCard, RiskLabel
from aura.fre.validate import normalize_weights, validate_probability, validate_weight


@dataclass
class FusionConfig:
    """Config for FRE-v2 fusion.

    Note: weights are validated + normalized inside `fuse_evidence` so callers
    can pass un-normalized weights as long as they're non-negative.
    """

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

    Validation:
    - probabilities must be in [0,1]
    - weights must be non-negative; if they don't sum to 1 we normalize them
    """

    p_prov_auth = validate_probability(p_prov_auth, name="p_prov_auth")
    p_forensic_synth = validate_probability(p_forensic_synth, name="p_forensic_synth")
    p_sem_anomaly = validate_probability(p_sem_anomaly, name="p_sem_anomaly")

    w_prov = validate_weight(cfg.w_prov, name="w_prov")
    w_forensic = validate_weight(cfg.w_forensic, name="w_forensic")
    w_sem = validate_weight(cfg.w_sem, name="w_sem")
    w_prov, w_forensic, w_sem = normalize_weights(w_prov, w_forensic, w_sem)

    risk_score = (
        w_prov * (1.0 - p_prov_auth) + w_forensic * p_forensic_synth + w_sem * p_sem_anomaly
    )

    # Confidence v1: distance from the undecided region + penalties for contradictions.
    # This is still heuristic, but it's less misleading than a raw transform.
    # - 0.5 => low confidence
    # - closer to 0 or 1 => higher confidence
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

    if contradictions:
        # Conservative: cap confidence when the streams disagree.
        confidence = min(confidence, 0.55)

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

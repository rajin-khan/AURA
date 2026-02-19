"""FRE-v2 stub runner.

This is *not* a finished detector. It's a practical scaffold that mirrors
`Reports/2026-Strategy-Update/Feb/Aura-Forensic-Risk-Engine-v2.md`.

Goal:
- make the pipeline shape explicit
- produce a stable "risk card" output schema
- provide a place to plug in provenance + forensics + semantics as they mature

Usage (from Code/):

  python -m aura.fre.run_fre_stub --input path/to/image.jpg
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from aura.fre.fusion import fuse_evidence
from aura.fre.schema import EvidenceItem


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Path to media (image for now)")

    # Allow injecting stream posteriors to test boundaries + downstream tooling.
    ap.add_argument("--p-provenance-auth", type=float, default=0.5, help="P(authentic | provenance) in [0,1]")
    ap.add_argument("--p-forensic-synth", type=float, default=0.5, help="P(synthetic | forensics) in [0,1]")
    ap.add_argument("--p-sem-anomaly", type=float, default=0.5, help="P(anomaly | semantics) in [0,1]")

    ap.add_argument("--out", type=str, default="-", help="Output path (default: stdout). Use '-' for stdout")
    args = ap.parse_args()

    p = Path(args.input)
    if not p.exists():
        raise SystemExit(f"Input not found: {p}")

    # Placeholder evidence — these will become real modules.
    p_prov_auth = args.p_provenance_auth
    p_forensic_synth = args.p_forensic_synth
    p_sem_anomaly = args.p_sem_anomaly

    evidence = [
        EvidenceItem(
            stream="provenance",
            name="provenance_gate",
            weight=0.45,
            score=1.0 - p_prov_auth,
            note="stub: no C2PA/provenance parser wired yet",
        ),
        EvidenceItem(
            stream="forensic",
            name="forensic_baseline",
            weight=0.40,
            score=p_forensic_synth,
            note="stub: plug displacement/PRNU/watermark here",
        ),
        EvidenceItem(
            stream="semantic",
            name="semantic_checks",
            weight=0.15,
            score=p_sem_anomaly,
            note="stub: do not use as sole trigger",
        ),
    ]

    card, contradictions = fuse_evidence(
        p_prov_auth=p_prov_auth,
        p_forensic_synth=p_forensic_synth,
        p_sem_anomaly=p_sem_anomaly,
        evidence=evidence,
    )

    out = {
        "input": str(p),
        "risk_card": card.to_dict(),
        "contradictions": contradictions,
    }

    payload = json.dumps(out, indent=2)

    if args.out == "-":
        print(payload)
    else:
        Path(args.out).write_text(payload + "\n", encoding="utf-8")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

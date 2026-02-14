"""AURA demo runner (Feb 2026).

Goal: one command that produces something you can *show*.

What it does:
1) Runs the FRE-v2 *stub* to produce a Risk Card JSON (pipeline shape).
2) Writes an artifact bundle into Code/runs/ (so progress is visible).

This does NOT claim detection accuracy. It is a scaffolding demo to:
- prove the output schema
- demonstrate conservative labeling / abstention
- create a reproducible artifact trail

Run:
  python scripts/demo.py --out runs/demo

Then show:
- runs/demo/risk_card.json
- runs/demo/SUMMARY.txt
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path

# Allow running as a plain script from Code/
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "src"))

from aura.fre.fusion import fuse_evidence
from aura.fre.schema import EvidenceItem


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, help="Output dir (e.g. runs/demo)")
    args = ap.parse_args()

    out_dir = Path(args.out)
    _ensure_dir(out_dir)

    # Demo scores intentionally sit in the inconclusive band.
    p_prov_auth = 0.50
    p_forensic_synth = 0.50
    p_sem_anomaly = 0.50

    evidence = [
        EvidenceItem(
            stream="provenance",
            name="provenance_gate",
            weight=0.45,
            score=1.0 - p_prov_auth,
            note="demo: no C2PA/provenance parser wired yet",
        ),
        EvidenceItem(
            stream="forensic",
            name="embedding_displacement_baseline",
            weight=0.40,
            score=p_forensic_synth,
            note="demo: placeholder score; run the displacement baseline for real artifacts",
        ),
        EvidenceItem(
            stream="semantic",
            name="semantic_checks",
            weight=0.15,
            score=p_sem_anomaly,
            note="demo: semantic is advisory only",
        ),
    ]

    card, contradictions = fuse_evidence(
        p_prov_auth=p_prov_auth,
        p_forensic_synth=p_forensic_synth,
        p_sem_anomaly=p_sem_anomaly,
        evidence=evidence,
    )

    payload = {
        "demo": True,
        "risk_card": card.to_dict(),
        "contradictions": contradictions,
        "notes": [
            "This is a scaffold demo, not an accuracy claim.",
            "Next: wire provenance parser + run displacement baseline on a paired dataset.",
        ],
    }

    (out_dir / "risk_card.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")

    (out_dir / "SUMMARY.txt").write_text(
        "\n".join(
            [
                "AURA demo run (Feb 2026)",
                f"output={out_dir}",
                f"label={card.label}",
                f"risk_score={card.risk_score:.3f}",
                f"confidence={card.confidence:.3f}",
                "Artifacts:",
                f"- {out_dir / 'risk_card.json'}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )

    print((out_dir / "SUMMARY.txt").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

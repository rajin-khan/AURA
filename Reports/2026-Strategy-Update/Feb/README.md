# Feb 2026 — Strategy Update (Source of Truth)

If you’re new to AURA and only have time for one folder, it’s this one.

This set of documents defines:
- what AURA is building,
- the decision policy (conservative + abstain),
- the *first practical implementation steps*,
- and how we will measure progress.

## Read order (recommended)

1) **Meeting brief** — the TL;DR and near-term steps
- `Meeting-Brief-Feb-10-2026.md`

2) **Forensic Risk Engine v2 (FRE-v2)** — the implementable pipeline
- `Aura-Forensic-Risk-Engine-v2.md`

3) **Embedding displacement idea** — the “first build” in practice
- `Aura-Embedding-Directions-Feasibility-2026.md`

4) **Benchmark protocol** — how we evaluate without overclaiming
- `Aura-Evaluation-Benchmark-Protocol-2026.md`

## Implementation mapping (what lives in Code/)

The codebase is being rewritten from scratch to match these docs.

- **Step 1 (minimal pipeline):**
  - CLIP embeddings + displacement `d = E(edited) - E(original)`
  - baseline classifier + artifacts
  - `Code/src/aura/forensics/`

- **FRE-v2 skeleton:**
  - provenance gate → forensic/semantic evidence → fusion → abstention
  - `Code/src/aura/fre/`

## What “done” means for the first milestone

A new contributor should be able to:
- read these docs,
- run **one command** that produces artifacts they can show,
- then run **one real baseline** on a paired dataset,
- and see a first, honest result + limitations.

### Commands (from `Code/`)

1) **Instant demo (no dataset required)**

```bash
make demo
```

Produces:
- `Code/runs/demo/risk_card.json`

2) **Real baseline (needs paired dataset + deps)**

```bash
pip install torch open_clip_torch pillow scikit-learn pandas
PYTHONPATH=src python -m aura.forensics.run_displacement_baseline \
  --manifest src/aura/data/paired_dataset/manifest.jsonl \
  --out runs/001
```

Produces:
- `Code/runs/001/metrics.json`
- `Code/runs/001/pairs_features.csv`

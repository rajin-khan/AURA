# AURA Code (Feb 2026 rewrite)

This `Code/` folder is a **fresh implementation from scratch** aligned to:
- `Reports/2026-Strategy-Update/Feb/`

If you are new:
1) read `../Reports/2026-Strategy-Update/Feb/README.md`
2) come back here and run the baseline.

## What exists right now

### 1) Minimal practical pipeline (Step 1)

Implements the meeting brief’s first deliverable:
> CLIP embeddings + displacement + baseline classifiers

Location:
- `src/aura/forensics/`

### 2) FRE-v2 skeleton

A small, explicit implementation scaffold for:
- provenance gate
- evidence fusion
- calibration + abstention

Location:
- `src/aura/fre/`

## Quickstart

### A) Create a paired dataset manifest

See:
- `src/aura/data/paired_dataset/README.md`

### B) Install deps

This repo intentionally keeps installation flexible (research-first).

```bash
pip install -r requirements.txt
```

### C) Run the displacement baseline

From inside `Code/`:

```bash
python -m aura.forensics.run_displacement_baseline \
  --manifest src/aura/data/paired_dataset/manifest.jsonl \
  --out runs/001 \
  --device cpu
```

Artifacts will be written under `Code/runs/`.

## Design rules (important)

- **Conservative outputs**: prefer *inconclusive* over overconfident.
- **Everything writes artifacts**: metrics JSON, features CSV/JSON, and a short SUMMARY.
- **The Feb docs are the contract**: if code diverges, we update code to match docs (or amend docs explicitly).

# GenImage Selection-to-Manifest Flow (2026)

**Date:** April 12, 2026  
**Status:** Intake plumbing note

## Why this exists

The earlier GenImage scaffold had one remaining awkward edge:
- the sampler selected files,
- but the registrar could still register all staged files.

That was structurally messy.

So the improved flow is now:

1. stage candidate files
2. run deterministic selection
3. register **only selected files** into the benchmark manifest

That is the correct data path.

---

## Commands

### Step 1 — deterministic selection

```bash
python scripts/data/sample_genimage_subset.py \
  --root Code/data/raw/public/genimage/subsets/genimage-mini-v1 \
  --out-dir Code/data/processed/genimage-mini-v1-selection
```

### Step 2 — manifest generation from selection lists

```bash
python scripts/data/register_benchmark_from_selection.py \
  --selection-dir Code/data/processed/genimage-mini-v1-selection \
  --dataset-name genimage-mini-v1 \
  --out Code/data/manifests/public/genimage-mini-v1.jsonl
```

---

## Why this is better

This flow ensures:
- manifests reflect the actual chosen subset,
- candidate overflow does not leak into the benchmark manifest,
- and the benchmark lane remains reproducible and clean.

---

## Practical recommendation

When real ingestion starts, use this path by default.

Do not register from the staged candidate pool unless there is a specific reason to preserve the larger candidate set separately.

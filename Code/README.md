# AURA Code (Feb 2026 rewrite)

This `Code/` folder is the **from-scratch implementation** of the Feb 2026 strategy docs.

Source-of-truth (read this first):
- `../Reports/2026-Strategy-Update/Feb/README.md`

If you’ve only read the Feb docs and you’re wondering “what can I actually run?” — this file answers that.

---

## What this codebase is (and isn’t)

### It *is*
- a practical, executable implementation scaffold for:
  - the **embedding displacement** idea (`d = E(edited) - E(original)`)
  - the **FRE-v2** risk engine shape (provenance + forensics + semantics → fusion → abstention)
- artifact-first: every run writes outputs you can show your instructor

### It is *not*
- a finished detection product
- an accuracy claim (yet)

---

## One-command demo (something to show immediately)

From inside `Code/`:

```bash
make venv
make demo
```

Outputs:
- `runs/demo/risk_card.json`
- `runs/demo/SUMMARY.txt`

What you can say to your instructor:
- “We implemented the FRE-v2 output schema + fusion rule and produce a stable Risk Card artifact bundle.”
- “Next, we’ll plug real provenance parsing + real forensic signals into the same interface.”

---

## What can be run today (real pipeline)

### 0) FRE-v2 stub runner (validated + testable)

```bash
make venv
make fre INPUT=path/to/file.jpg
```

You can also inject stream posteriors to test decision boundaries:

```bash
. .venv/bin/activate
python -m aura.fre.run_fre_stub \
  --input path/to/file.jpg \
  --p-provenance-auth 0.95 \
  --p-forensic-synth 0.10 \
  --p-sem-anomaly 0.20
```

### 1) Displacement baseline (Step 1 from meeting brief)

Implements:
> CLIP embeddings + displacement + baseline classifiers

Code:
- `src/aura/forensics/`

#### Setup

This repo uses a virtualenv for editable installs (PEP 668 on Debian blocks system-wide pip installs).

```bash
make venv
```

(Equivalent: `python -m venv .venv && . .venv/bin/activate && pip install -e .`)

Install required deps (if you’re not using the editable install route):

```bash
pip install -r requirements.txt
```

Install optional research deps (needed for the baseline):

```bash
pip install torch open_clip_torch pillow scikit-learn pandas
```

#### Data

Legacy toy example:
- `src/aura/data/paired_dataset/README.md`

New data-engine layout:
- `data/README.md`
- `data/manifests/paired/example_pairs.v1.jsonl`

You’ll need paired examples:
- original → cosmetic edit
- original → AI edit

Validate a manifest:

```bash
make validate-manifest MANIFEST=data/manifests/paired/example_pairs.v1.jsonl
```

Generate deterministic splits:

```bash
make make-splits \
  MANIFEST=data/manifests/paired/example_pairs.v1.jsonl \
  OUT=data/processed/splits/example_pairs.with_splits.jsonl
```

#### Run

```bash
PYTHONPATH=src python -m aura.forensics.run_displacement_baseline \
  --manifest src/aura/data/paired_dataset/manifest.jsonl \
  --out runs/001 \
  --device cpu
```

Artifacts produced (show these):
- `runs/001/metrics.json`
- `runs/001/pairs_features.csv` (or `pairs_features.json`)
- `runs/001/SUMMARY.txt`

---

## Datasets you can use (actionable options)

The Feb benchmark doc suggests a mixed strategy:

### A) “Internal paired set” (best for displacement)

Create your own small paired dataset (even 50–200 pairs is enough to start):
- take real photos (phone)
- make cosmetic edits (crop, exposure, denoise)
- make AI edits (inpaint, insert/remove objects)

Why it’s helpful:
- labels are clean because *you controlled the edit*
- displacement geometry becomes measurable

### B) Public datasets (good for baseline comparisons)

Good starting points (you can use subsets):
- GenImage (AI vs real)
- FaceForensics++ / DFDC (video/frame-based)

Caveat:
- many are not “paired original→edited” by default, so displacement is harder unless you construct pairs.

---

## Data engine (new)

Aura now includes a first-pass data engine scaffold for paired manifests:

- `src/aura/data_engine/schema.py` — canonical pair sample schema
- `src/aura/data_engine/manifest.py` — manifest load/write helpers
- `src/aura/data_engine/validate.py` — validation logic
- `src/aura/data_engine/splits.py` — deterministic split assignment
- `scripts/data/validate_manifest.py` — CLI validator
- `scripts/data/make_splits.py` — CLI split generator
- `src/aura/data_engine/benchmark_schema.py` — public benchmark sample schema
- `src/aura/data_engine/benchmark_manifest.py` — benchmark manifest helpers
- `scripts/data/register_genimage_subset.py` — register a local GenImage subset into a benchmark manifest

This is not the full retrieval/editing automation yet.
It is the first practical layer that makes that automation possible.

## GenImage subset intake (new)

Planned local staging location:
- `data/raw/public/genimage/`

When a small local subset exists, register it like this:

```bash
PYTHONPATH=src python scripts/data/register_genimage_subset.py \
  --root data/raw/public/genimage/subsets/genimage-mini-v1 \
  --dataset-name genimage-mini-v1 \
  --out data/manifests/public/genimage-mini-v1.jsonl
```

This gives Aura a benchmark manifest for GenImage without pretending it is a true original→edited pair dataset.

## Progress checklist (what to show your instructor)

### Week 1 — runnable scaffold + artifacts
- [x] Feb docs made source-of-truth (`Reports/.../Feb/README.md`)
- [x] FRE-v2 output schema implemented (`src/aura/fre/`)
- [x] one-command demo produces Risk Card artifact (`make demo`)

### Week 2 — first real signal
- [ ] curate 50–200 paired samples (cosmetic vs ai)
- [ ] run displacement baseline and show:
  - `pairs_features.csv`
  - first accuracy/AUC (or honest note if sample size small)

### Week 3 — tighten scientific story
- [ ] add subspace projection features (PCA + residual norm)
- [ ] add 1–2 plots (UMAP + calibration curve) as artifacts

---

## Design rules (non-negotiable)

- **Conservative outputs**: prefer *inconclusive* over overconfident.
- **Artifacts every run**: metrics JSON + features + summary.
- **The Feb docs are the contract**: if code diverges, code changes (or docs amended explicitly).

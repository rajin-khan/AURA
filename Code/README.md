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

### 1) Displacement baseline (Step 1 from meeting brief)

Implements:
> CLIP embeddings + displacement + baseline classifiers

Code:
- `src/aura/forensics/`

#### Setup

Install required deps:

```bash
pip install -r requirements.txt
```

Install optional research deps (needed for the baseline):

```bash
pip install torch open_clip_torch pillow scikit-learn pandas
```

#### Data

Create a paired dataset manifest:
- `src/aura/data/paired_dataset/README.md`

You’ll need paired examples:
- original → cosmetic edit
- original → AI edit

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

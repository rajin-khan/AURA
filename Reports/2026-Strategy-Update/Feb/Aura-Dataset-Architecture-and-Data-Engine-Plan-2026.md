# Aura Dataset Architecture and Data Engine Plan (2026)

**Date:** April 12, 2026  
**Status:** Working draft

> [!IMPORTANT]
> Aura’s next bottleneck is not model complexity. It is data infrastructure.

## Why this document exists

The current Aura codebase already has:

- a practical displacement baseline,
- a manifest format for paired samples,
- and a clear research direction.

What it does **not** yet have is a proper data engine.

That means the immediate highest-leverage work is to define how Aura will:

- acquire images,
- organize originals and edits,
- record labels and provenance,
- generate controlled edits,
- produce benchmark splits,
- and store reproducible run inputs.

Without this layer, model iteration will be slow, inconsistent, and difficult to defend scientifically.

---

## Design principle

We should treat Aura’s data system as **three connected lanes**, not one blob.

### Lane A — Public benchmark lane

Purpose:
- baseline coverage,
- external comparison,
- robustness sanity checks.

Examples:
- GenImage
- OpenFake
- Deepfake-Eval-style collections
- FaceForensics++ / DFDC frames where appropriate

What this lane gives us:
- breadth,
- domain variety,
- baseline detector comparison.

What it does **not** reliably give us:
- clean original→edited pair structure.

### Lane B — Controlled paired-edit lane

Purpose:
- test the core displacement hypothesis,
- measure cosmetic vs AI edit geometry,
- support cleaner scientific claims.

This is the most important lane for the near-term Aura contribution.

Examples:
- original photo → crop/exposure/tone version,
- original photo → inpainting/removal/insertion version,
- original photo → mixed human + AI edit version.

What this lane gives us:
- controlled labels,
- clean pair semantics,
- direct support for `d = E(edited) - E(original)`.

### Lane C — Stress and robustness lane

Purpose:
- measure whether signals survive real-world pipelines.

Examples:
- JPEG recompression ladder,
- resize/downscale/upscale,
- screenshot recapture,
- social-platform transcode approximations,
- metadata stripping,
- anti-forensic perturbation tests.

This lane is crucial for calibration, abstention analysis, and honest reporting.

---

## Recommended repo structure

The current repo stores a tiny paired example under:

- `Code/src/aura/data/paired_dataset/`

That is fine as a toy example, but it is too narrow for the actual data workflow.

Recommended evolution:

```text
Code/
  data/
    raw/
      public/
      internal/
    paired/
      originals/
      edits/
    manifests/
      paired/
      public/
      stress/
    processed/
      splits/
      features/
    stress/
      jpeg/
      resize/
      transcode/
      recapture/
```

### Interpretation

- `data/raw/`
  - immutable source assets or imported dataset subsets
  - never hand-edited
- `data/paired/`
  - the clean working area for original/edited pair construction
- `data/manifests/`
  - canonical JSONL/CSV definitions of samples
- `data/processed/`
  - generated splits and derived artifacts
- `data/stress/`
  - transformed variants for robustness evaluation

> [!NOTE]
> Large datasets should still be gitignored and optionally tracked through DVC, Git LFS, or external storage later. The key point now is shape and reproducibility.

---

## Minimal canonical sample schema

The current manifest format is intentionally tiny:

```json
{"id":"0001","original_path":"...","edited_path":"...","label":"cosmetic","notes":"crop + tone"}
```

That was enough for the first baseline, but not enough for a real data engine.

Recommended canonical schema fields:

```json
{
  "id": "pair-0001",
  "dataset": "aura-internal-v1",
  "split": "train",
  "domain": "natural-image",
  "source_type": "internal-controlled",
  "original_path": "data/paired/originals/0001.jpg",
  "edited_path": "data/paired/edits/0001_ai_inpaint.jpg",
  "label": "ai",
  "edit_family": "inpaint-removal",
  "edit_tool": "gemini-edit",
  "edit_intent": "remove-object",
  "is_paired": true,
  "stress_parent": null,
  "license": "internal-research-only",
  "notes": "bench removed from background"
}
```

### Fields we should care about immediately

- `id`
- `dataset`
- `split`
- `original_path`
- `edited_path`
- `label`
- `edit_family`
- `source_type`
- `domain`
- `notes`

### Label vocabulary

Near-term allowed labels:
- `cosmetic`
- `ai`
- `mixed`
- `unknown`

### Edit family vocabulary (starter)

- `crop`
- `exposure-color`
- `retouch`
- `denoise-sharpen`
- `inpaint-removal`
- `object-insertion`
- `relighting`
- `face-alteration`
- `background-change`
- `style-transfer`
- `mixed-edit`

This gives us much better analysis later than a flat binary label alone.

---

## What automation should exist

Aura needs a small but disciplined data engine.

### 1) Import / retrieval tools

Scripts should be able to:
- ingest public dataset subsets,
- normalize folder names,
- copy or symlink into Aura’s expected structure,
- emit manifest rows automatically.

Suggested future script family:

- `scripts/data/import_public_dataset.py`
- `scripts/data/register_dataset.py`
- `scripts/data/build_manifest.py`

### 2) Controlled editing tools

Scripts should be able to:
- take an original image,
- run one or more edit operations,
- save outputs in deterministic locations,
- record the operation in metadata.

This can start with simple transforms first:
- crop,
- resize,
- JPEG recompress,
- brightness/contrast,
- blur,
- denoise.

Then later add AI-edit hooks:
- inpainting,
- object insertion,
- relighting,
- style transfer.

Suggested future script family:

- `scripts/data/make_cosmetic_edits.py`
- `scripts/data/make_stress_variants.py`
- `scripts/data/run_ai_edits.py`

### 3) Validation tools

We should validate before every run:
- file paths exist,
- labels are allowed,
- required fields are present,
- no duplicate IDs,
- no train/test leakage,
- paired semantics are intact.

Suggested script:
- `scripts/data/validate_manifest.py`

### 4) Split generation tools

We should not handcraft splits forever.

Need deterministic generation for:
- train
- val
- test
- optional domain holdout
- optional edit-family holdout

Suggested script:
- `scripts/data/make_splits.py`

---

## What not to do yet

We should **not** prematurely build:

- full DVC infrastructure,
- production-scale orchestration,
- a giant all-in-one pipeline script,
- benchmark dashboards before data contracts are stable.

That would be architecture cosplay.

The next step is smaller and more useful:
- define the schema,
- define the folders,
- define the scripts,
- then start feeding in real data.

---

## Recommended execution order

### Phase 1 — Data contract

Deliverables:
- this architecture doc,
- canonical manifest schema,
- starter script plan,
- updated `Code/README.md` pointers.

### Phase 2 — Dataset scouting and fit analysis

Deliverables:
- ranked shortlist of public datasets,
- what each dataset is good for,
- what each dataset is bad for,
- licensing/access friction notes,
- whether it supports paired displacement directly, indirectly, or not at all.

### Phase 3 — Minimal data engine implementation

Deliverables:
- manifest validator,
- split generator,
- first import helper,
- first cosmetic/stress edit generator.

### Phase 4 — AI editing automation

Deliverables:
- pluggable edit runners,
- operation logging,
- automatic manifest updates,
- reproducible paired set generation.

Only after these phases should we invest heavily in more advanced modeling.

---

## Sharp recommendation

If the goal is to make Aura actually move, the smartest next move is:

1. finalize the data architecture,
2. choose the first 2–4 datasets,
3. implement the smallest useful data engine,
4. then start curating controlled pair generation.

That path is clean, defensible, and actually aligned with the displacement idea.

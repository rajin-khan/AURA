# GenImage Ingestion Runbook v1 (2026)

**Date:** April 12, 2026  
**Status:** Pre-download operational runbook

## Purpose

This runbook defines the exact operational flow to ingest the first GenImage subset into Aura once we decide to actually pull files.

The goal is to avoid:
- random folder chaos,
- accidental oversized downloads,
- undocumented sampling,
- and one-off manual decisions we can’t reproduce later.

---

## Scope

This runbook is for:
- `genimage-mini-v1`

It assumes we want:
- `2,000 real`
- `250 synthetic per generator`
- `4,000 total images`

It does **not** cover full-dataset ingestion.

---

## Inputs

Verified source links:

- Repo: <https://github.com/GenImage-Dataset/GenImage>
- Project page: <https://genimage-dataset.github.io/>
- Google Drive: <https://drive.google.com/drive/folders/1jGt10bwTbhEZuGXLyvrCuxOI0cBqQ1FS?usp=sharing>
- Baidu: <https://pan.baidu.com/s/1i0OFqYN5i6oFAxeK6bIwRQ>

Expected generators:
- `adm`
- `biggan`
- `glide`
- `midjourney`
- `stable_diffusion_v1_4`
- `stable_diffusion_v1_5`
- `vqdm`
- `wukong`

---

## Workspace targets

### Staging root

```text
Code/data/raw/public/genimage/subsets/genimage-mini-v1/
```

### Required subfolders

```text
real/
synthetic/adm/
synthetic/biggan/
synthetic/glide/
synthetic/midjourney/
synthetic/stable_diffusion_v1_4/
synthetic/stable_diffusion_v1_5/
synthetic/vqdm/
synthetic/wukong/
```

### Output artifacts

```text
Code/data/processed/genimage-mini-v1-selection/
Code/data/manifests/public/genimage-mini-v1.jsonl
```

---

## Actual flow

### Step 1 — Inspect source structure before pulling anything large

Before download/import:
- inspect how the public distribution is organized
- confirm where real images live
- confirm per-generator folder naming
- confirm whether class folders are exposed clearly

If the upstream naming differs from our canonical local layout, normalize locally during staging.

---

### Step 2 — Stage only what we need

Do **not** pull the entire dataset.

Instead:
- identify enough files to satisfy:
  - `2,000 real`
  - `250 per generator`
- optionally stage a small buffer above target if source traversal makes exact selection awkward

Recommended practical buffer:
- up to `10–20%` extra staged candidates per bucket if needed

But do not let this balloon.

---

### Step 3 — Normalize into Aura layout

Map staged files into:

```text
genimage-mini-v1/real/<class-or-bucket>/...
genimage-mini-v1/synthetic/<generator>/<class-or-bucket>/...
```

Rules:
- preserve original filenames where practical
- avoid renaming unless collision handling requires it
- keep class/category folder names if available

---

### Step 4 — Run deterministic subset selection

Use the policy/scaffolded script:

```bash
python scripts/data/sample_genimage_subset.py \
  --root Code/data/raw/public/genimage/subsets/genimage-mini-v1 \
  --out-dir Code/data/processed/genimage-mini-v1-selection
```

Expected outputs:
- `selected_real.txt`
- `selected_<generator>.txt`
- `summary.json`

This step determines the exact chosen subset using seed `20260412`.

---

### Step 5 — Register manifest

After selection is finalized, register the local subset into a benchmark manifest:

```bash
python scripts/data/register_genimage_subset.py \
  --root Code/data/raw/public/genimage/subsets/genimage-mini-v1 \
  --dataset-name genimage-mini-v1 \
  --out Code/data/manifests/public/genimage-mini-v1.jsonl
```

Note:
- current scaffold registers all staged images, not only the selected ones
- when moving from scaffold to actual ingestion, we should either:
  - stage only the final selected subset, or
  - extend the registrar to read selection lists

### Recommendation
For the cleanest first pass:
- stage only the selected final subset in the canonical tree

That avoids unnecessary ambiguity.

---

### Step 6 — Generate splits

Once the benchmark manifest reflects the final selected subset:
- generate splits later using the benchmark-lane split tooling (or extend current tooling if needed)

For v1, desired split policy is:
- `70 / 15 / 15`
- label-balanced at minimum
- generator-aware if practical

---

## Validation checklist

Before calling ingestion complete, verify:

- [ ] real count == 2,000
- [ ] each generator count == 250
- [ ] total synthetic count == 2,000
- [ ] total dataset count == 4,000
- [ ] folder layout matches canonical structure
- [ ] sampling seed recorded as `20260412`
- [ ] benchmark manifest exists
- [ ] no obvious corrupt/non-image junk in staged subset

---

## Practical warnings

### Do not do this
- don’t ingest the whole Drive folder
- don’t mix raw download dumps with final subset folders
- don’t pretend GenImage entries are original→edited pairs
- don’t silently rebalance generators if one bucket is short

### Do this instead
- fail loudly on quota shortfalls
- document deviations
- preserve benchmark honesty

---

## Best next implementation upgrade

Before actual download day, the most useful code upgrade would be:

- a selector/registrar flow that can:
  1. stage candidate pools,
  2. emit selected file lists,
  3. and generate a manifest from the selected lists only.

That would eliminate the remaining ambiguity in the current scaffold.

---

## Final recommendation

When we are ready to do the first real intake, the cleanest sequence is:

1. inspect upstream layout
2. stage only needed GenImage candidates
3. normalize into Aura’s canonical subset tree
4. run deterministic selection
5. register the final subset manifest
6. validate counts and move on to benchmarking

That gives Aura a disciplined public benchmark lane without turning ingestion into a mess.

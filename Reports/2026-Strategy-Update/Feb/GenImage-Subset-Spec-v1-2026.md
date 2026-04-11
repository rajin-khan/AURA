# GenImage Subset Spec v1 (2026)

**Date:** April 12, 2026  
**Status:** First operational subset specification

## Goal

Define the first practical GenImage slice Aura should ingest **before** any download begins.

This spec exists so we do not:
- download too much,
- create a messy folder structure,
- or accidentally produce an unbalanced benchmark subset.

---

## What this subset is for

This is **not** Aura’s core scientific dataset.

This subset is for:
- a public benchmark lane,
- baseline real-vs-AI evaluation,
- generator diversity sanity checks,
- and validating our intake/manifest/split pipeline.

---

## Dataset name

Recommended first dataset ID:

- `genimage-mini-v1`

This name should be used in:
- folder names,
- benchmark manifests,
- experiment notes,
- and split outputs.

---

## Generator selection

Use all major generators already visible in the verified public distribution:

- `adm`
- `biggan`
- `glide`
- `midjourney`
- `stable_diffusion_v1_4`
- `stable_diffusion_v1_5`
- `vqdm`
- `wukong`

### Why all 8?

Because the point of this first subset is not just accuracy.
It is generator coverage.

Using all 8 gives Aura:
- broad synthetic diversity,
- better generalization sanity checks,
- and cleaner future reporting.

---

## Real-image side

Use a matched real-image pool with the same total scale as the synthetic side.

Recommended target:
- one unified real pool rather than trying to create fake one-to-one pair semantics.

This keeps the benchmark honest.

---

## Recommended image counts

### Minimum viable subset
- **100 synthetic images per generator**
- 8 generators → **800 synthetic images total**
- **800 real images total**
- **1,600 images overall**

### Better first subset
- **250 synthetic images per generator**
- 8 generators → **2,000 synthetic images total**
- **2,000 real images total**
- **4,000 images overall**

### Upper bound for first pass
- **500 synthetic images per generator**
- 8 generators → **4,000 synthetic images total**
- **4,000 real images total**
- **8,000 images overall**

---

## Recommendation

Use the **better first subset**:

- **250 per generator**
- **2,000 real**
- **4,000 total**

Why:
- large enough to matter,
- still manageable,
- not stupidly huge for a first operational pass.

---

## Class handling

If class/category metadata is naturally present in the staged files:
- preserve it in the manifest as `class_name`

If not:
- do not block intake on perfect class balancing for v1
- prioritize generator balance first

So the priority order is:
1. generator balance
2. real vs synthetic balance
3. class balance (nice-to-have, not blocker)

---

## Folder layout

Recommended local staging layout:

```text
Code/data/raw/public/genimage/subsets/genimage-mini-v1/
  real/
    <class-or-bucket>/
      *.jpg
  synthetic/
    adm/
      <class-or-bucket>/
        *.jpg
    biggan/
      <class-or-bucket>/
        *.jpg
    glide/
      <class-or-bucket>/
        *.jpg
    midjourney/
      <class-or-bucket>/
        *.jpg
    stable_diffusion_v1_4/
      <class-or-bucket>/
        *.jpg
    stable_diffusion_v1_5/
      <class-or-bucket>/
        *.jpg
    vqdm/
      <class-or-bucket>/
        *.jpg
    wukong/
      <class-or-bucket>/
        *.jpg
```

### Why this layout

It makes label detection straightforward:
- anything under `real/` → `label=real`
- anything under `synthetic/<generator>/` → `label=synthetic`, `generator=<generator>`

This is much cleaner than inferring labels from random legacy folders later.

---

## Split strategy

Recommended first split:
- `70% train`
- `15% val`
- `15% test`

Split constraints:
- stratify by `label`
- later extend to stratify by `generator` where practical

For v1, avoiding gross imbalance is more important than perfect statistical elegance.

---

## Manifest expectations

Each registered item should capture:
- `id`
- `dataset`
- `split`
- `image_path`
- `label`
- `generator`
- `source_type`
- `domain`
- `class_name`
- `notes`

This keeps GenImage properly modeled as a benchmark dataset rather than a fake pair dataset.

---

## What not to do

Do **not**:
- pretend GenImage is original→edited pair data
- download the full dataset immediately
- over-optimize class balancing before we have a working intake path
- mix staged raw files with processed benchmark subsets

That would create chaos for almost no benefit.

---

## Final recommendation

Aura should adopt this first operational GenImage target:

- dataset id: `genimage-mini-v1`
- generators: all 8 verified generators
- synthetic count: `250 each`
- total synthetic: `2,000`
- total real: `2,000`
- total images: `4,000`
- layout: `real/` + `synthetic/<generator>/...`

That is the cleanest first benchmark slice.

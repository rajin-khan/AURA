# GenImage Subset Intake Plan (2026)

**Date:** April 12, 2026  
**Status:** Initial implementation plan

## Why GenImage first

GenImage is currently the strongest first public dataset target for Aura because it is:

- publicly reachable,
- directly downloadable in principle,
- broad across multiple generators,
- and useful for Aura’s baseline real-vs-AI lane.

It is **not** the perfect fit for Aura’s core pair-displacement idea, but it is the best verified public starting point.

---

## Goal

Do **not** ingest the full dataset first.

Instead, build a **subset-first intake path** that:
- records provenance,
- normalizes file locations,
- creates a manifest,
- and gives Aura a reproducible baseline slice.

---

## Proposed first subset

### Real images
- small, class-balanced subset from the real side

### Synthetic images
- small, generator-balanced subset from:
  - Midjourney
  - Stable Diffusion v1.4
  - Stable Diffusion v1.5
  - ADM
  - GLIDE
  - VQDM
  - Wukong
  - BigGAN

### Suggested first scale
- **100–250 images per generator** for the first operational pass
- plus matched/parallel real-image count

This is enough to:
- validate the import path,
- test manifest generation,
- and benchmark Aura quickly without melting the Pi.

---

## Proposed repo placement

```text
Code/data/
  raw/
    public/
      genimage/
        README.md
        subsets/
          genimage-mini-v1/
  manifests/
    public/
      genimage-mini-v1.jsonl
  processed/
    splits/
      genimage-mini-v1.with_splits.jsonl
```

---

## Manifest semantics for GenImage

GenImage is not a true original→edited pair dataset.

So for Aura we should treat it as:
- a **public benchmark lane** dataset,
- with `source_type="public-benchmark"`,
- and with pseudo-pair semantics disabled or abstracted.

Two options exist:

### Option A — force it into pair schema (not ideal)
Create pseudo-pairs that map a real image to a generator sample from the same class.

Problem:
- not true edit provenance,
- scientifically weaker for displacement claims.

### Option B — support a benchmark manifest variant (better)
Represent GenImage entries as benchmark samples with fields like:
- `id`
- `dataset`
- `split`
- `image_path`
- `label`
- `generator`
- `source_type`
- `domain`
- `notes`

This is the cleaner route.

---

## Recommended implementation order

1. add a **dataset registration note** for GenImage
2. add a **subset manifest builder** script
3. add a **public benchmark schema** if needed
4. add split generation for benchmark entries
5. later connect this into Aura baselines

---

## Sharp recommendation

The first GenImage milestone should be:

- **not download everything**
- **not over-design storage**
- **just make a tiny, reproducible, documented subset path**

That gets Aura moving fast without turning data intake into a swamp.

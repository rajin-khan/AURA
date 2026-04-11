# Aura Dataset Scouting and Fit Analysis (2026)

**Date:** April 12, 2026  
**Status:** Working draft

> [!IMPORTANT]
> Public datasets are useful for Aura, but they will not replace a controlled paired-edit dataset.

## Why this memo exists

Aura’s core near-term idea is not generic deepfake detection.
It is the hypothesis that edit displacement in embedding space carries useful structure:

`d = E(edited) - E(original)`

That means we should evaluate datasets by one main question:

**Do they help Aura’s pair-based displacement story, or are they only useful for broader baseline coverage?**

The answer matters because some popular datasets are large and famous but still a poor fit for Aura’s core scientific contribution.

---

## Evaluation criteria

Each dataset below is judged on:

- fit for **real-vs-AI baseline** work,
- fit for **paired original→edited displacement** work,
- fit for **robustness / manipulation stress** work,
- access friction,
- and overall strategic value.

---

## 1) GenImage

### What it is

GenImage is presented as a **million-scale benchmark for detecting AI-generated images**.
From the project materials, it includes over one million real/AI examples and spans multiple generators, including:

- Midjourney
- Stable Diffusion
- ADM
- GLIDE
- Wukong
- VQDM
- BigGAN

It uses aligned ImageNet-style class structure and is explicitly intended for AI-image detection benchmarking.

### Why it is attractive

GenImage is probably the best immediate public dataset for Aura’s **baseline real-vs-AI lane**.

Why:
- large scale,
- multiple generators,
- broad category coverage,
- established benchmark visibility.

### Where it helps Aura

Strong use cases:
- binary real-vs-AI baselines,
- detector comparison sanity checks,
- generator generalization analysis,
- stress-testing whether simple displacement features carry any useful signal even without strict edit pairs.

### Where it does **not** solve Aura’s problem

GenImage is not really a clean **original→edited** dataset in the Aura sense.
It is much better understood as:
- real image set,
- AI image set,
- sometimes semantically aligned by class,
- but not necessarily a true “before/after edit of the same image” resource.

That means it is **excellent for baseline coverage** but only **medium-fit** for the core displacement hypothesis.

### Practical caveats

- large storage footprint,
- access/distribution friction,
- likely overkill to ingest in full on the Pi.

### Verdict

**Use it, but as a subset-first benchmark lane, not as Aura’s main scientific foundation.**

### Aura fit score

- Real-vs-AI baseline: **High**
- Pair-based displacement: **Medium**
- Robustness lane: **Medium**
- Overall strategic value: **High**

---

## 2) FaceForensics++

### What it is

FaceForensics++ is a major manipulated-face benchmark built from original videos plus multiple manipulation methods.
The official materials describe:
- original video sequences,
- multiple automated manipulation methods,
- masks,
- and associated download tooling.

### Why it matters

Unlike generic AI-image datasets, FaceForensics++ has much cleaner manipulation structure.
That makes it much more useful for Aura’s **manipulation lane** than many broad “AI-generated image” datasets.

### Where it helps Aura

Strong use cases:
- frame extraction for manipulated vs original comparisons,
- testing whether displacement captures manipulation families,
- robustness experiments around compression/transcoding,
- segmentation-aware analysis later if desired.

### Where it falls short

- highly face-centric,
- video-first,
- not a broad natural-image benchmark,
- less aligned with non-face image editing use cases.

So it helps Aura scientifically, but it should not become the whole story.

### Practical caveats

- gated / request-style access,
- operational friction,
- may require frame extraction and additional preprocessing.

### Verdict

**Very useful as a manipulation/stress lane dataset, but too narrow to serve as Aura’s main data source.**

### Aura fit score

- Real-vs-AI baseline: **Medium**
- Pair-based displacement: **Medium**
- Robustness / manipulation lane: **High**
- Overall strategic value: **Medium-High**

---

## 3) DFDC / Deep Fake Detection Dataset family

### What it is

The DeepFake Detection Challenge ecosystem and related Google/Jigsaw dataset family remain common external benchmarks for deepfake detection.
They are useful mostly as broad external evaluation references.

### Where it helps Aura

- transfer testing,
- frame-level generalization checks,
- benchmarking against well-known face deepfake data.

### Where it falls short

- face/video heavy,
- not cleanly aligned to pair-based image editing,
- weak fit for Aura’s broader authenticity + provenance framing.

### Verdict

**Useful as a secondary benchmark family, not a priority dataset for the next implementation phase.**

### Aura fit score

- Real-vs-AI baseline: **Medium**
- Pair-based displacement: **Low**
- Robustness lane: **Medium**
- Overall strategic value: **Medium-Low**

---

## 4) OpenFake

### What it is

OpenFake is described in its paper listing as an **open dataset and platform toward real-world deepfake detection**, with emphasis on politically grounded and modern generative content.

### Why it is interesting

This makes it appealing for Aura because it sounds more realistic and contemporary than older closed-world benchmarks.

### Where it helps Aura

Potential use cases:
- out-of-distribution realism checks,
- in-the-wild benchmark validation,
- external credibility when reporting results beyond lab-style data.

### Where it falls short

From quick scouting, it does not appear to be a strong fit for strict original→edited pairing.
That makes it more of a **generalization benchmark** than a core development dataset.

Access path is also less clear from a quick pass, which increases near-term friction.

### Verdict

**Promising later-stage benchmark, but not the first dataset to operationalize.**

### Aura fit score

- Real-vs-AI baseline: **Medium-High**
- Pair-based displacement: **Low**
- Robustness lane: **Medium**
- Overall strategic value: **Medium**

---

## Bottom line: what public datasets are actually good for in Aura

Public datasets are most useful for three things:

### A) Baseline detector coverage
Especially:
- real vs AI discrimination,
- transfer/generalization checks,
- external comparison.

### B) Manipulation robustness
Especially:
- compression,
- video-to-frame artifacts,
- known forgery families,
- face-centric manipulation studies.

### C) External credibility
Using established benchmarks helps Aura avoid looking like a project that only works on its own homemade data.

---

## What public datasets do **not** solve

They do **not** fully solve Aura’s core scientific need:

- clean original→edited pairing,
- edit-family control,
- cosmetic vs AI labeling with low ambiguity,
- reproducible stress pipelines built from the same base image.

That is why Aura still needs an **internal controlled paired-edit dataset**.

Without that lane, the displacement idea stays under-tested.

---

## Recommended first dataset stack for Aura

If we optimize for actual progress instead of benchmark hoarding, the best first stack is:

### Tier 1 — must have

1. **Internal controlled paired set**
   - this is the core Aura lane
   - supports the displacement hypothesis directly

2. **GenImage subset**
   - gives immediate real-vs-AI benchmark coverage
   - use a subset first, not the full monster

### Tier 2 — strong add-on

3. **FaceForensics++ subset / extracted frames**
   - gives manipulation-family and robustness value
   - useful especially if Aura later wants manipulation typing

### Tier 3 — later realism benchmark

4. **OpenFake**
   - useful for external realism/generalization once the core lane is stable

---

## Sharp recommendation

The smartest move is:

1. build Aura around a **controlled internal paired-edit dataset**,
2. add **GenImage subset ingestion** for baseline coverage,
3. add **FaceForensics++ subset/frame pipeline** for manipulation stress,
4. postpone broader benchmark expansion until the data engine exists.

That keeps the project aligned with its real novelty instead of drifting into generic benchmark chasing.

---

## Source pointers

Useful source pointers identified during scouting:

- GenImage project page / repo materials:
  - `https://github.com/GenImage-Dataset/GenImage`
  - `https://genimage-dataset.github.io/`
- FaceForensics / FaceForensics++ materials:
  - `https://github.com/ondyari/FaceForensics`
  - `https://arxiv.org/abs/1901.08971`
- OpenFake paper listing:
  - arXiv search listing for *OpenFake: An Open Dataset and Platform Toward Real-World Deepfake Detection*

These sources are enough to support next-step planning, though some datasets may still require access handling later.

# GenImage Sampling Policy v1 (2026)

**Date:** April 12, 2026  
**Status:** Operational policy before any download/import

## Purpose

This policy defines how Aura should choose samples for `genimage-mini-v1`.

The goal is simple:
- make the first subset **reproducible**,
- reasonably balanced,
- and useful enough for benchmarking,
- without pretending we need perfect dataset curation on day one.

---

## Dataset target

Working subset:
- `genimage-mini-v1`

Target scale:
- **2,000 real images**
- **2,000 synthetic images**
- **4,000 total images**

Synthetic allocation:
- **250 images per generator**

Generators:
- `adm`
- `biggan`
- `glide`
- `midjourney`
- `stable_diffusion_v1_4`
- `stable_diffusion_v1_5`
- `vqdm`
- `wukong`

---

## Main balancing priorities

Priority order:

1. **generator balance**
2. **real vs synthetic balance**
3. **approximate class balance**
4. **per-class perfection**

This order matters.

If we try to optimize everything at once on the first pass, we’ll waste time and overcomplicate intake.

---

## Real-image sampling policy

### Target
- sample **2,000 real images total**

### Rule
- spread the real images across as many available classes/categories as practical
- prefer **class-aware balanced sampling** if class folders are available
- otherwise use reproducible random sampling from the full real pool

### Recommended class-aware rule
If class folders exist:
- compute available classes
- sample approximately equal counts per class
- if exact divisibility fails, distribute remainder deterministically by sorted class name

This gives us a subset that is not skewed to a tiny handful of categories.

---

## Synthetic-image sampling policy

### Target
- sample **250 images per generator**

### Rule
For each generator:
- use the same balancing logic independently
- prefer class-aware balanced sampling if class folders exist
- otherwise use reproducible random sampling within that generator’s pool

This ensures every generator contributes equally.

---

## Reproducibility rule

### Fixed seed
Use a fixed sampling seed for v1:
- **seed = 20260412**

This seed should be recorded in:
- script defaults,
- manifests,
- and experiment notes.

If we later make a new sample version, change the dataset id rather than silently changing the seed.

---

## Deterministic ordering rule

Before sampling:
- enumerate files in **sorted path order**
- then apply the RNG/shuffle with the fixed seed

Why:
- filesystem traversal can otherwise be nondeterministic
- sorted input + fixed seed = reproducible output

---

## Replacement rule

Sampling should be:
- **without replacement**

If a class/generator bucket has fewer items than requested:
- take all available items
- log the shortfall
- redistribute remaining quota across other eligible buckets deterministically

---

## Shortfall handling

### Example
If one generator has only 180 usable staged images but target is 250:
- take the 180
- note a shortfall of 70
- do **not** silently hallucinate balance
- either:
  - redistribute within that generator across remaining classes if possible, or
  - record the subset as underfilled and stop

For v1, honesty beats fake neatness.

### Recommended v1 behavior
- fail loudly if a generator total is below the requested quota
- do not auto-rebalance across generators

Why:
- generator equality is more important than forcing total count at all costs

---

## Class-balance tolerance

Perfect class parity is not required for v1.

Use this tolerance mindset:
- **good enough:** broad category spread, no obvious collapse into a few classes
- **not acceptable:** one or two classes dominate a generator subset by accident

If class metadata exists, we should use it.
If not, we should not block the whole pipeline on that limitation.

---

## Exclusion policy

Exclude files that are:
- unreadable/corrupt
- duplicates by exact path identity in the staged subset
- obviously non-image files
- temporary or hidden system artifacts

Do **not** try to solve semantic duplicate detection yet.
That is future work.

---

## Naming / manifest notes

Every selected item should preserve enough metadata to reconstruct its origin:
- dataset id
- label (`real` or `synthetic`)
- generator (if synthetic)
- class name if available
- original staged path
- sampling seed used for the subset

---

## Recommended implementation behavior

When we later script the actual sampler, it should:

1. scan staged files
2. summarize counts by label/generator/class
3. verify quotas are feasible
4. sample deterministically with seed `20260412`
5. emit:
   - selected file list
   - benchmark manifest
   - short summary report

That report should say things like:
- real pool size
- per-generator pool size
- selected counts
- any shortfalls
- whether class-aware balancing was applied

---

## Final recommendation

For `genimage-mini-v1`, Aura should use:

- **seed:** `20260412`
- **real target:** `2,000`
- **synthetic target:** `250 per generator`
- **sampling mode:** deterministic, without replacement
- **balancing mode:**
  - generator-balanced first
  - class-aware when available
  - otherwise reproducible random sampling

That gives us a first subset that is disciplined, explainable, and reproducible.

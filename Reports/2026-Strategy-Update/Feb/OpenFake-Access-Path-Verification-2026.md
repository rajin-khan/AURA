# OpenFake Access Path Verification (2026)

**Date:** April 12, 2026  
**Status:** Verified follow-up pass

## Main finding

OpenFake does in fact have a public GitHub repository:

- Repo: <https://github.com/vicliv/OpenFake>

This is a meaningful upgrade from the earlier scouting pass, where we had only verified the paper listing.

---

## What the repo claims

From the current `README.md` in the repo:

- It presents OpenFake as:
  - an open dataset,
  - a platform toward large-scale deepfake detection,
  - with multiple detection baselines,
  - and scripts for synthetic image generation.

It explicitly links to:

- Hugging Face dataset page: <https://huggingface.co/datasets/CDL-AMLRT/OpenFake>
- Imagen 3 test set: <https://drive.google.com/file/d/1hd-cfhkn2eTI6Aj-XdbNHa1M2vcbfjqa/view?usp=share_link>
- Stable Diffusion 2.1 test set: <https://drive.google.com/file/d/1l4Om1ta28rZkqFxdaFm2DlEwKN19vzfM/view?usp=share_link>

---

## What is actually verified

### Verified real and reachable
- GitHub repository exists and loads publicly.
- The repo appears active enough to be taken seriously.
- The repo contains:
  - `baselines/`
  - `dataset/`
  - `README.md`
  - `requirements.txt`

### Verified concerning / incomplete
- The linked Hugging Face dataset page currently returns **404**:
  - <https://huggingface.co/datasets/CDL-AMLRT/OpenFake>
- That means the most obvious direct dataset distribution path is currently broken or private/unpublished.

### Partially verified
- The README includes direct Google Drive links for two test sets:
  - Imagen 3 test set
  - Stable Diffusion 2.1 test set
- In this pass, we verified the links are present in the README, but we have **not yet opened/downloaded those files**.

### Additional repo evidence
- The `dataset/` directory does **not** appear to contain the dataset itself.
- It contains helper/generation scripts instead:
  - `generate_SD3.py`
  - `generate_flux.py`
  - `laion_filtering.py`
  - `requirements.txt`

This strongly suggests the repo is more of a **construction / benchmark / baseline repo** than a self-contained downloadable dataset release.

---

## Practical interpretation for Aura

OpenFake is now more credible than before because:
- the code repo is real,
- it includes baselines,
- it references actual test-set downloads,
- and the project structure is coherent.

But it is also still operationally messy because:
- the primary Hugging Face dataset link is broken,
- there is no clearly verified working full-dataset portal yet,
- and the repo appears to rely in part on reconstruction / generation scripts rather than a fully packaged public release.

---

## Verdict

### Is OpenFake real?
- **Yes.**

### Is there a verified public code repo?
- **Yes.**

### Is there a verified public full-dataset download path?
- **Not reliably.**
- The most obvious official link currently fails.

### Are there some directly linked downloadable resources?
- **Probably yes**, via the README’s Google Drive test-set links.
- But the main full dataset path is still not fully operationally verified.

### Is it useful for Aura?
- **Yes, likely useful for realism/generalization benchmarking.**
- Still not the cleanest first ingestion target.

---

## Updated recommendation

OpenFake should move from:
- **"unclear / maybe"**

to:
- **"real and promising, but operationally unstable as a first acquisition target"**

So the working priority remains:
1. **GenImage**
2. **FaceForensics++**
3. **OpenFake**

OpenFake is worth keeping on the board, but not worth betting the first ingestion pipeline on.

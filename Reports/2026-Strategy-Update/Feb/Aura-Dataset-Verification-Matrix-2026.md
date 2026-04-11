# Aura Dataset Verification Matrix (2026)

**Date:** April 12, 2026  
**Status:** Verified link-access pass (no downloads performed)

> [!IMPORTANT]
> This pass verifies whether candidate datasets appear real, reachable, gated, publicly downloadable, or too uncertain to prioritize.

## Summary table

### 1) GenImage

- **Direct project/repo:** <https://github.com/GenImage-Dataset/GenImage>
- **Project page:** <https://genimage-dataset.github.io/>
- **Google Drive dataset folder:** <https://drive.google.com/drive/folders/1jGt10bwTbhEZuGXLyvrCuxOI0cBqQ1FS?usp=sharing>
- **Baidu dataset link (from repo):** <https://pan.baidu.com/s/1i0OFqYN5i6oFAxeK6bIwRQ>

**Verification result**
- Repo loads.
- Project page exists.
- Google Drive folder opens publicly.
- Visible generator folders confirm that the dataset distribution is real and organized.

**Usable?**
- Yes.

**Downloadable right now?**
- Yes, in principle, via Google Drive / Baidu.
- Still large enough that we should subset, not blindly ingest.

**Useful for Aura?**
- Yes — strong for baseline real-vs-AI work.

**Limits for Aura**
- Not a clean original→edited pair dataset.
- Better for external benchmark coverage than the core displacement hypothesis.

**Aura verdict**
- **Highest-priority public dataset to target first**.

---

### 2) FaceForensics++

- **Official repo:** <https://github.com/ondyari/FaceForensics>
- **Paper:** <https://arxiv.org/abs/1901.08971>
- **Access / request form:** <https://docs.google.com/forms/d/e/1FAIpQLSdRRR3L5zAv6tQ_CKxmK4W96tAab_pfBu2EKAgQbeDVhmXagg/viewform>

**Verification result**
- Repo loads.
- Paper page is live.
- Google Form access page is real and reachable.

**Usable?**
- Yes.

**Downloadable right now?**
- Not immediately.
- Access is gated behind the request form / approval flow.

**Useful for Aura?**
- Yes — especially for manipulation-family and robustness/stress evaluation.

**Limits for Aura**
- Face/video-centric.
- Not broad natural-image edit coverage.

**Aura verdict**
- **Very useful second-priority dataset**, but operationally gated.

---

### 3) OpenFake

- **Paper page:** <https://arxiv.org/abs/2509.09495>
- **Search listing:** <https://arxiv.org/search/?query=OpenFake%3A+An+Open+Dataset+and+Platform+Toward+Real-World+Deepfake+Detection&searchtype=all&source=header>
- **DOI:** <https://doi.org/10.48550/arXiv.2509.09495>

**Verification result**
- arXiv paper page is real and accessible.
- The abstract explicitly claims:
  - nearly 4M total images,
  - ~3M real images with captions,
  - ~1M synthetic counterparts.
- However, I did **not** verify a public dataset landing page or working download portal in this pass.

**Usable?**
- Probably, but not yet operationally confirmed.

**Downloadable right now?**
- **Unverified.**

**Useful for Aura?**
- Likely yes for realism/generalization benchmarking.

**Limits for Aura**
- Unclear access path.
- Still weaker than a true controlled pair dataset for the core Aura claim.

**Aura verdict**
- **Promising but not yet acquisition-ready**.

---

### 4) DFDC (Deepfake Detection Challenge)

- **Kaggle competition page:** <https://www.kaggle.com/competitions/deepfake-detection-challenge>

**Verification result**
- Kaggle competition page loads publicly.
- Competition is clearly real and archived.
- However, the verified page mostly confirms competition existence and historical context, not immediate open dataset intake simplicity.

**Usable?**
- Yes, historically and as a benchmark reference.

**Downloadable right now?**
- Partially / conditionally.
- Likely tied to Kaggle competition/data access constraints and account workflow.
- Not as straightforward as GenImage from this pass.

**Useful for Aura?**
- Moderately useful for external deepfake benchmarking.

**Limits for Aura**
- Face/video-heavy.
- Not great for pair-based image displacement.

**Aura verdict**
- **Lower priority than GenImage and FaceForensics++**.

---

## Broken / weak leads found during verification

### FaridLab Hugging Face DeepfakeDetection page
- Attempted path returned **404**.
- Not reliable as a current acquisition target.

### Random DFDC GitHub repo lead (`jtths/dfdc`)
- Returned **404 / invalid lead**.
- Not trustworthy.

---

## Practical ranking after verification

### Best immediately actionable
1. **GenImage**

### Best high-value but gated
2. **FaceForensics++**

### Best promising but access-uncertain
3. **OpenFake**

### Best legacy benchmark reference
4. **DFDC**

---

## Recommendation

If we want the cleanest next move without downloading anything yet:

1. plan for a **GenImage subset intake path**,
2. prepare the **FaceForensics++ request/application step**,
3. investigate whether **OpenFake exposes a dataset portal/repo/contact route**,
4. treat DFDC as optional benchmark support, not the first operational target.

That ordering gives us the highest ratio of usefulness to friction.

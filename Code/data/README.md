# Aura datasets and why this folder looks like this

This folder is where Aura’s **data side** lives.

If the current structure looks a little more “engineered” than a normal class project folder, that’s on purpose.

We are trying to avoid the classic research-project failure mode:
- files scattered everywhere,
- random one-off scripts,
- unclear labels,
- impossible-to-reproduce experiments,
- and six weeks later nobody remembers what dataset version was actually used.

So this README explains, in plain English:
- why we made manifests and other “fancy” things,
- which datasets we explored,
- where the links are,
- why we picked some and not others,
- and why the folder structure exists.

---

## The simple version

Aura is about authenticity / manipulation / AI-image detection.

That means the project needs data in **two different styles**:

### 1) Paired data
This is the ideal Aura data.

Example:
- original image
- edited version of the **same** image

Why it matters:
- this supports Aura’s core idea of comparing:
  - the original image,
  - the edited image,
  - and the **difference** between them in embedding space

This is why there is a `paired/` area and a paired manifest format.

### 2) Public benchmark data
This is the practical benchmark layer.

Example:
- real images from a benchmark
- AI-generated images from a benchmark
- but **not** true before/after pairs

Why it matters:
- it helps us evaluate Aura against public datasets
- it gives broader coverage across generators and styles
- it makes the work more credible than testing only on our own custom data

This is why we added a **benchmark manifest** path instead of forcing every dataset into fake pair structure.

---

## Why manifests exist

A manifest is just a structured list of dataset entries.

In simple terms, it says:
- what files exist
- where they are
- what label they have
- what split they belong to
- and any useful metadata

### Why not just use folders?
Because folders alone are too weak.

Folders don’t clearly record:
- which exact subset we selected
- which version of the dataset we used
- train / val / test split membership
- generator name
- edit family
- notes or provenance

A manifest solves that.

### Why this matters for Aura
Without manifests, we would eventually hit these problems:
- “Which 4,000 images did we use again?”
- “Was this result from the full staged pool or the sampled subset?”
- “Was this image real, synthetic, cosmetic edit, or AI edit?”
- “Did we accidentally leak test samples into train?”

So yes, manifests look slightly more formal — but they save our ass later.

---

## Why there are multiple folders

### `raw/`
For source datasets or staged subsets.

Think of this as:
- “the files we got from outside”
- or “the local staging area before/while we process them”

### `paired/`
For clean original/edited Aura pairs.

This is the important lane for Aura’s actual research contribution.

### `manifests/`
For the structured metadata files that describe what the dataset really is.

### `processed/`
For outputs created from raw/staged data:
- sample lists
- splits
- features
- derived exports

### `stress/`
For robustness variants later:
- resize
- recompression
- transcode
- recapture-like artifacts

This separation is mostly about **not making a mess**.

---

## Datasets we explored

We did a verification pass before downloading anything.
That was intentional.

We did **not** want to blindly commit to a dataset and later find out:
- the link is dead,
- access is gated,
- the dataset is huge and impractical,
- or it doesn’t actually fit Aura well.

So we looked at several candidates first.

---

# Dataset shortlist

## 1) GenImage

### Direct links
- Repo: <https://github.com/GenImage-Dataset/GenImage>
- Project page: <https://genimage-dataset.github.io/>
- Google Drive: <https://drive.google.com/drive/folders/1jGt10bwTbhEZuGXLyvrCuxOI0cBqQ1FS?usp=sharing>
- Baidu: <https://pan.baidu.com/s/1i0OFqYN5i6oFAxeK6bIwRQ>

### How it was found
We found it through standard dataset scouting for AI-image detection benchmarks and then verified it directly by:
- opening the repo,
- checking the project page,
- and visiting the actual public dataset links.

### What it is
GenImage is a large benchmark for **real vs AI-generated images**.

It includes multiple generators, including:
- ADM
- BigGAN
- GLIDE
- Midjourney
- Stable Diffusion v1.4
- Stable Diffusion v1.5
- VQDM
- Wukong

### Why it is useful
This is currently the best first public benchmark target for Aura because it gives us:
- multiple generators
- broad synthetic diversity
- realistic baseline benchmarking value
- a public source we can actually access

### What it is **not**
It is **not** a true original→edited pair dataset.

That means it is useful for:
- real-vs-AI benchmarking
- generator generalization checks
- public benchmark coverage

But it is **not** the perfect dataset for Aura’s core displacement idea.

### How big is it?
Big enough that we should **not** download the whole thing casually.

Exact byte size can vary depending on the distribution path and what parts we use, but it is clearly large enough that:
- full ingestion would be overkill right now
- subset-first is the sane choice

### Why we can use it
Because:
- the links are real
- the Google Drive is public
- the generators are visible
- and it is benchmark-relevant

### Feasibility score
- **9/10** as a first public benchmark target

### Why that score?
- strong usefulness
- directly accessible
- public links verified
- only downside is size and the fact that it is not true paired-edit data

### Why we chose it first
Because it hits the sweet spot of:
- useful
- reachable
- credible
- and practical enough to subset

This is why `GenImage` became our first public dataset target.

---

## 2) FaceForensics++

### Direct links
- Repo: <https://github.com/ondyari/FaceForensics>
- Paper: <https://arxiv.org/abs/1901.08971>
- Access/request form: <https://docs.google.com/forms/d/e/1FAIpQLSdRRR3L5zAv6tQ_CKxmK4W96tAab_pfBu2EKAgQbeDVhmXagg/viewform>

### How it was found
This is a standard manipulation/deepfake benchmark, so it came up naturally during dataset scouting for forensic/manipulation datasets.
We then verified:
- the repo,
- the paper,
- and the request form.

### What it is
A well-known face manipulation benchmark.
It is stronger for manipulation/fake-face evaluation than generic AI-image datasets.

### Why it is useful
Useful for:
- manipulation-family evaluation
- robustness/stress testing
- face-centric forgery analysis

### What it is **not**
It is not a broad natural-image editing dataset.
It is also more video/face oriented than Aura’s broader long-term ambition.

### How big is it?
Large enough and structured enough that we should not treat it as a casual plug-and-play dataset.
Also, access is gated.

### Why we can use it
We *can* use it, but not immediately.
It requires request/approval flow.

### Feasibility score
- **6.5/10** for near-term use

### Why that score?
- scientifically useful
- but operationally gated
- narrower domain
- not the easiest first ingestion target

### Why we did **not** choose it first
Because the access friction is higher than GenImage and the scope is narrower.

---

## 3) OpenFake

### Direct links
- Repo: <https://github.com/vicliv/OpenFake>
- Paper: <https://arxiv.org/abs/2509.09495>
- DOI: <https://doi.org/10.48550/arXiv.2509.09495>
- README-linked HF dataset path: <https://huggingface.co/datasets/CDL-AMLRT/OpenFake>
- Imagen 3 test set: <https://drive.google.com/file/d/1hd-cfhkn2eTI6Aj-XdbNHa1M2vcbfjqa/view?usp=share_link>
- SD 2.1 test set: <https://drive.google.com/file/d/1l4Om1ta28rZkqFxdaFm2DlEwKN19vzfM/view?usp=share_link>

### How it was found
Initially from paper/arXiv scouting, then later we dug further and found the actual public repo.

### What it is
A newer benchmark/platform around large-scale deepfake / AI-image detection.
The repo includes:
- baselines
- generation/helper scripts
- dataset references

### Why it is useful
Potentially useful for:
- realism/generalization benchmarking
- newer generator coverage
- external comparison beyond older benchmarks

### What is the catch?
The main Hugging Face dataset link in the repo currently returns **404**.

That means:
- the project is real
- the repo is real
- but the most obvious full dataset path is currently broken/unavailable

### How big is it?
The paper/repo positioning suggests it is large-scale.
Practical issue is less about raw size and more about **access reliability** right now.

### Why we might use it later
Because it still looks scientifically relevant.
But it is not the most stable first operational target.

### Feasibility score
- **5.5/10** right now

### Why that score?
- real project
- useful benchmark direction
- but broken main dataset link is a serious operational problem

### Why we did **not** choose it first
Because “interesting but unstable” is the wrong first dependency.

---

## 4) DFDC (Deepfake Detection Challenge)

### Direct link
- Kaggle competition page: <https://www.kaggle.com/competitions/deepfake-detection-challenge>

### How it was found
This is one of the classic benchmark families in deepfake detection, so it came up naturally in baseline scouting.

### What it is
A major historical deepfake benchmark with public benchmark importance.

### Why it is useful
Useful as:
- historical reference benchmark
- external comparison point
- face/video manipulation benchmark family

### What it is **not**
Not a strong fit for Aura’s core pair-based image displacement story.
Also more awkward operationally than GenImage for our first public intake.

### Feasibility score
- **5/10** for the immediate next step

### Why that score?
- benchmark value exists
- but it is less aligned and less convenient than GenImage

---

# Why we made the current decisions

## Why not just download everything?
Because that would be dumb for a first pass.

Problems with downloading everything immediately:
- too much storage
- too much clutter
- no clear benchmark version
- harder to explain what was actually used
- higher chance of unusable garbage accumulating in the repo structure

So we decided to go **subset-first**.

---

## Why `genimage-mini-v1`?
Because we wanted a first benchmark slice that is:
- useful enough to matter
- small enough to manage
- reproducible
- easy to explain in a paper / report / meeting

So we chose:
- **2,000 real images**
- **250 synthetic images per generator**
- **8 generators**
- **4,000 images total**

That is big enough to be serious, but not so big that intake becomes a swamp.

---

## Why the sampling policy exists
Because if we later ask:
- “Why these images?”
- “Can we reproduce this subset?”
- “Did we bias the benchmark accidentally?”

we need an answer better than “uhhhh I clicked around in Drive and copied some folders.”

So the policy says:
- fixed seed
- deterministic selection
- generator balance first
- class-aware when available
- no fake balancing bullshit

That makes the subset defendable.

---

## Why selection lists and manifests both exist
Because they solve different problems.

### Selection lists
These answer:
- which exact files were chosen?

### Manifest
This answers:
- what are these files?
- what labels do they have?
- what dataset version are they part of?
- what split do they belong to?

The clean pipeline is:
1. stage candidate files
2. sample deterministically
3. register only selected files into the manifest

That is why the current design looks a bit formal.
It is trying to be **clean and reproducible**, not fancy for its own sake.

---

# Current recommendation

If somebody asks “What should Aura use first?” the answer right now is:

## First public benchmark target
- **GenImage**

## First manipulation-focused add-on later
- **FaceForensics++**

## Keep watching but don’t rely on yet
- **OpenFake**

## Lower-priority reference benchmark
- **DFDC**

---

# Final takeaway

Everything in this folder is basically here for one reason:

> we want Aura’s data workflow to be understandable, reproducible, and sane.

Not overcomplicated.
Not sloppy.
Just solid enough that future-us doesn’t hate present-us.

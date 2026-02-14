# Paired mini-dataset (Aura internal)

This folder is a **starter spec** for the Feb 2026 practical implementation.

The research docs explicitly call for a paired dataset:
- real capture → cosmetic edit
- real capture → AI edit

Why paired matters:
- our key signal is **edit displacement** in embedding space:

`d = E(edited) - E(original)`

## Folder structure (suggested)

You can organize files however you want, as long as the manifest paths resolve.
A simple approach:

- `original/`
- `edited/`

## Manifest format

Create `manifest.jsonl` where each line is one JSON object:

```json
{"id":"0001","original_path":"data/paired_dataset/original/0001.jpg","edited_path":"data/paired_dataset/edited/0001_cosmetic.jpg","label":"cosmetic","notes":"crop + slight tone"}
{"id":"0002","original_path":"data/paired_dataset/original/0002.jpg","edited_path":"data/paired_dataset/edited/0002_ai.jpg","label":"ai","notes":"inpainted object removal"}
```

Allowed labels (baseline supports only `cosmetic` and `ai`):
- `cosmetic`
- `ai`
- `mixed`
- `unknown`

## Running the baseline

From the `Code/` directory:

```bash
python -m forensics.run_displacement_baseline \
  --manifest data/paired_dataset/manifest.jsonl \
  --out runs/001 \
  --device cpu
```

### Optional deps

The baseline requires optional packages:

```bash
pip install torch open_clip_torch pillow scikit-learn pandas
```

If you have a GPU machine later, set `--device cuda`.

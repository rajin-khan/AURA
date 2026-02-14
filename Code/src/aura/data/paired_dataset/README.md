# Paired mini-dataset (internal)

This is the minimal dataset shape needed to run the **Feb 2026 displacement baseline**.

The key signal we’re testing is:

`d = E(edited) - E(original)`

So we need **paired** examples.

## Manifest format

Create `manifest.jsonl` where each line is one JSON object:

```json
{"id":"0001","original_path":"src/aura/data/paired_dataset/original/0001.jpg","edited_path":"src/aura/data/paired_dataset/edited/0001_cosmetic.jpg","label":"cosmetic","notes":"crop + tone"}
{"id":"0002","original_path":"src/aura/data/paired_dataset/original/0002.jpg","edited_path":"src/aura/data/paired_dataset/edited/0002_ai.jpg","label":"ai","notes":"inpaint removal"}
```

Allowed labels:
- `cosmetic`
- `ai`
- `mixed`
- `unknown`

## Where to put images

Do **not** commit private images.

You can store them anywhere locally; the manifest just needs correct paths.

## Run

From `Code/`:

```bash
python -m aura.forensics.run_displacement_baseline \
  --manifest src/aura/data/paired_dataset/manifest.jsonl \
  --out runs/001
```

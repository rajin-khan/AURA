# Aura data layout

This folder holds the next-step data engine structure for Aura.

## Planned subfolders

- `raw/`
  - immutable source data or imported subsets
- `paired/`
  - clean original/edited working pairs
- `manifests/`
  - canonical JSONL manifests
- `processed/`
  - derived splits/features/exports
- `stress/`
  - robustness variants (jpeg, resize, transcode, recapture)

## Current guidance

- Keep large datasets out of git.
- Track only tiny examples or schemas in the repository.
- Prefer manifests as the source of truth for experiment inputs.

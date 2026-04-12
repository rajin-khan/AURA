# GenImage intake notes

This folder is reserved for locally staged GenImage subsets.

## Status

No dataset has been downloaded yet.

## Planned workflow

1. stage a tiny verified subset under this tree
2. use the canonical subset layout under `subsets/genimage-mini-v1/`
3. run `scripts/data/register_genimage_subset.py`
4. emit a benchmark manifest under `data/manifests/public/`
5. generate train/val/test splits later

## Canonical first subset layout

```text
subsets/genimage-mini-v1/
  real/
  synthetic/
    adm/
    biggan/
    glide/
    midjourney/
    stable_diffusion_v1_4/
    stable_diffusion_v1_5/
    vqdm/
    wukong/
```

## Direct source links

- Repo: https://github.com/GenImage-Dataset/GenImage
- Project page: https://genimage-dataset.github.io/
- Google Drive: https://drive.google.com/drive/folders/1jGt10bwTbhEZuGXLyvrCuxOI0cBqQ1FS?usp=sharing
- Baidu: https://pan.baidu.com/s/1i0OFqYN5i6oFAxeK6bIwRQ

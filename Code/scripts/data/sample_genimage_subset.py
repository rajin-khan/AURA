from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
import random

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}
GENERATORS = [
    "adm",
    "biggan",
    "glide",
    "midjourney",
    "stable_diffusion_v1_4",
    "stable_diffusion_v1_5",
    "vqdm",
    "wukong",
]
DEFAULT_SEED = 20260412


def list_images(root: Path) -> list[Path]:
    return sorted(
        p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in IMAGE_EXTS
    )


def grouped_by_class(paths: list[Path]) -> dict[str, list[Path]]:
    out: dict[str, list[Path]] = defaultdict(list)
    for p in paths:
        cls = p.parent.name if p.parent != p.parent.parent else "_root"
        out[cls].append(p)
    return {k: sorted(v) for k, v in sorted(out.items())}


def balanced_sample(paths: list[Path], target: int, seed: int) -> list[Path]:
    if len(paths) < target:
        raise ValueError(f"pool has only {len(paths)} items but target is {target}")

    rng = random.Random(seed)
    groups = grouped_by_class(paths)
    class_names = sorted(groups)
    n_classes = len(class_names)
    if n_classes == 0:
        return []

    base = target // n_classes
    remainder = target % n_classes

    selected: list[Path] = []
    leftovers: list[Path] = []

    for i, cls in enumerate(class_names):
        quota = base + (1 if i < remainder else 0)
        items = list(groups[cls])
        rng.shuffle(items)
        take = min(len(items), quota)
        selected.extend(items[:take])
        leftovers.extend(items[take:])

    if len(selected) < target:
        rng.shuffle(leftovers)
        need = target - len(selected)
        selected.extend(leftovers[:need])

    if len(selected) != target:
        raise ValueError(f"could not fulfill target {target}; got {len(selected)}")

    return sorted(selected)


def write_list(paths: list[Path], out: Path) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(str(p) for p in paths) + ("\n" if paths else ""), encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True, help="Path to genimage-mini-v1 staged subset root")
    ap.add_argument("--out-dir", required=True, help="Where to write selection reports")
    ap.add_argument("--real-target", type=int, default=2000)
    ap.add_argument("--per-generator", type=int, default=250)
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED)
    args = ap.parse_args()

    root = Path(args.root).resolve()
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    real_root = root / "real"
    synthetic_root = root / "synthetic"

    real_pool = list_images(real_root)
    selected_real = balanced_sample(real_pool, args.real_target, args.seed)
    write_list(selected_real, out_dir / "selected_real.txt")

    summary = {
        "seed": args.seed,
        "real_target": args.real_target,
        "per_generator": args.per_generator,
        "real_pool": len(real_pool),
        "generators": {},
    }

    for idx, gen in enumerate(GENERATORS):
        gen_root = synthetic_root / gen
        gen_pool = list_images(gen_root)
        gen_seed = args.seed + idx + 1
        selected = balanced_sample(gen_pool, args.per_generator, gen_seed)
        write_list(selected, out_dir / f"selected_{gen}.txt")
        summary["generators"][gen] = {
            "pool": len(gen_pool),
            "selected": len(selected),
            "seed": gen_seed,
        }

    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

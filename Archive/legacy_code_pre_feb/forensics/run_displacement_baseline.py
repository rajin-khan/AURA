"""Run the Feb 2026 displacement baseline end-to-end.

This is the *first practical implementation* of the strategy docs:
- embed image pairs using CLIP
- compute displacement features d = E(edited) - E(original)
- train a small linear classifier (cosmetic vs ai)
- output metrics + a CSV artifact you can inspect

Usage (from Code/):

  python -m forensics.run_displacement_baseline \
    --manifest data/paired_dataset/manifest.jsonl \
    --out runs/001

Optional extras:
  pip install torch open_clip_torch scikit-learn pandas

"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np

from forensics.clip_embedder import ClipConfig, ClipEmbedder
from forensics.displacement_features import compute_displacement_features, vectorize
from forensics.paired_manifest import load_manifest_jsonl


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _label_to_y(label: str) -> int:
    if label == "cosmetic":
        return 0
    if label == "ai":
        return 1
    raise ValueError(f"This baseline expects binary labels cosmetic/ai. Got: {label}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True, help="Path to manifest.jsonl")
    ap.add_argument("--out", required=True, help="Output dir for artifacts")
    ap.add_argument("--backend", default="open_clip", choices=["open_clip", "transformers"])
    ap.add_argument("--model", default="ViT-B-32", help="CLIP model id (backend-dependent)")
    ap.add_argument("--pretrained", default="laion2b_s34b_b79k", help="open_clip pretrained tag")
    ap.add_argument("--device", default="cpu")
    ap.add_argument(
        "--include-raw",
        action="store_true",
        help="Append the raw displacement vector to scalar features",
    )
    ap.add_argument("--seed", type=int, default=42)

    args = ap.parse_args()

    out_dir = Path(args.out)
    _ensure_dir(out_dir)

    records = load_manifest_jsonl(args.manifest)

    # Filter to binary baseline labels.
    records = [r for r in records if r.label in ("cosmetic", "ai")]
    if len(records) < 2:
        raise SystemExit("Need at least 2 labeled pairs (cosmetic/ai) to run")

    embedder = ClipEmbedder(
        ClipConfig(
            backend=args.backend,
            model=args.model,
            pretrained=args.pretrained,
            device=args.device,
        )
    )

    X: List[np.ndarray] = []
    y: List[int] = []
    rows: List[Dict] = []

    for rec in records:
        e0 = embedder.embed_image_path(rec.original_path)
        e1 = embedder.embed_image_path(rec.edited_path)
        feats = compute_displacement_features(e0, e1)
        v, idx = vectorize(feats, include_raw=args.include_raw)

        X.append(v)
        y.append(_label_to_y(rec.label))

        rows.append(
            {
                "id": rec.id,
                "label": rec.label,
                "original_path": rec.original_path,
                "edited_path": rec.edited_path,
                **feats.to_dict(),
            }
        )

    Xn = np.stack(X, axis=0)
    yn = np.array(y, dtype=np.int64)

    metrics: Dict = {
        "n": int(len(yn)),
        "include_raw": bool(args.include_raw),
        "backend": args.backend,
        "model": args.model,
    }

    # If we don't have enough pairs to properly split, we still write feature artifacts.
    if len(yn) < 6:
        metrics["note"] = (
            "Not enough labeled pairs for a meaningful train/test split. "
            "Add more samples to run the classifier baseline."
        )
        metrics["n_train"] = 0
        metrics["n_test"] = 0
        metrics["accuracy"] = None
        metrics["auc"] = None
        metrics["report"] = None
    else:
        # Simple train/test split.
        rng = np.random.default_rng(args.seed)
        perm = rng.permutation(len(yn))
        split = int(0.8 * len(yn))
        tr_idx = perm[:split]
        te_idx = perm[split:]

        X_tr, y_tr = Xn[tr_idx], yn[tr_idx]
        X_te, y_te = Xn[te_idx], yn[te_idx]

        try:
            from sklearn.linear_model import LogisticRegression
            from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
        except Exception as e:
            raise ImportError(
                "Missing deps for baseline training. Install: pip install scikit-learn"
            ) from e

        clf = LogisticRegression(max_iter=2000)
        clf.fit(X_tr, y_tr)

        probs = clf.predict_proba(X_te)[:, 1]
        pred = (probs >= 0.5).astype(np.int64)

        metrics["n_train"] = int(len(y_tr))
        metrics["n_test"] = int(len(y_te))

        try:
            metrics["auc"] = float(roc_auc_score(y_te, probs))
        except Exception:
            metrics["auc"] = None

        metrics["accuracy"] = float(accuracy_score(y_te, pred))
        metrics["report"] = classification_report(y_te, pred, output_dict=True)

    # Write artifacts.
    (out_dir / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    try:
        import pandas as pd

        df = pd.DataFrame(rows)
        df.to_csv(out_dir / "pairs_features.csv", index=False)
    except Exception:
        # pandas optional
        (out_dir / "pairs_features.json").write_text(json.dumps(rows, indent=2), encoding="utf-8")

    # Tiny human-readable summary.
    acc_line = (
        f"accuracy={metrics['accuracy']:.4f}" if isinstance(metrics.get("accuracy"), float) else "accuracy=N/A"
    )
    auc_line = f"auc={metrics['auc']}" if metrics.get("auc") is not None else "auc=N/A"

    lines = [
        "Aura displacement baseline run",
        f"n={metrics['n']} train={metrics.get('n_train')} test={metrics.get('n_test')}",
        f"backend={metrics['backend']} model={metrics['model']}",
        f"include_raw={metrics['include_raw']}",
        acc_line,
        auc_line,
    ]
    if metrics.get("note"):
        lines.append(f"note={metrics['note']}")

    (out_dir / "SUMMARY.txt").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print((out_dir / "SUMMARY.txt").read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

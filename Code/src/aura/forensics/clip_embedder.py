from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

import numpy as np


@dataclass
class ClipConfig:
    """CLIP embedding extraction configuration."""

    backend: Literal["open_clip", "transformers"] = "open_clip"
    # open_clip: model tag like "ViT-B-32"
    # transformers: model id like "openai/clip-vit-base-patch32"
    model: str = "ViT-B-32"
    # open_clip only
    pretrained: str = "laion2b_s34b_b79k"
    device: str = "cpu"


class ClipEmbedder:
    """Extract L2-normalized CLIP image embeddings.

    This is a deliberately small adapter so we can:
    - swap embedding backends
    - keep the rest of the pipeline stable

    Optional deps:
    - open_clip backend: torch, open_clip_torch, pillow
    - transformers backend: torch, transformers, pillow
    """

    def __init__(self, config: Optional[ClipConfig] = None):
        self.config = config or ClipConfig()

        if self.config.backend == "open_clip":
            self._init_open_clip()
        elif self.config.backend == "transformers":
            self._init_transformers()
        else:
            raise ValueError(f"Unknown backend: {self.config.backend}")

    def _init_open_clip(self):
        try:
            import torch
            import open_clip
            from PIL import Image
        except Exception as e:
            raise ImportError(
                "Missing deps for open_clip backend. Install: pip install torch open_clip_torch pillow"
            ) from e

        self.torch = torch
        self.Image = Image
        self.open_clip = open_clip

        model, _, preprocess = open_clip.create_model_and_transforms(
            self.config.model,
            pretrained=self.config.pretrained,
            device=self.config.device,
        )
        model.eval()

        self.model = model
        self.preprocess = preprocess

    def _init_transformers(self):
        try:
            import torch
            from PIL import Image
            from transformers import CLIPModel, CLIPProcessor
        except Exception as e:
            raise ImportError(
                "Missing deps for transformers backend. Install: pip install torch transformers pillow"
            ) from e

        self.torch = torch
        self.Image = Image
        self.CLIPModel = CLIPModel
        self.CLIPProcessor = CLIPProcessor

        model_id = self.config.model
        model = CLIPModel.from_pretrained(model_id)
        processor = CLIPProcessor.from_pretrained(model_id)
        model.to(self.config.device)
        model.eval()

        self.model = model
        self.processor = processor

    def embed_image_path(self, path: str) -> np.ndarray:
        if self.config.backend == "open_clip":
            img = self.Image.open(path).convert("RGB")
            x = self.preprocess(img).unsqueeze(0).to(self.config.device)

            with self.torch.no_grad():
                features = self.model.encode_image(x)
                features = features / features.norm(dim=-1, keepdim=True)

            return features.detach().cpu().numpy().astype(np.float32)[0]

        # transformers backend
        img = self.Image.open(path).convert("RGB")
        inputs = self.processor(images=img, return_tensors="pt")
        inputs = {k: v.to(self.config.device) for k, v in inputs.items()}

        with self.torch.no_grad():
            features = self.model.get_image_features(**inputs)
            features = features / features.norm(dim=-1, keepdim=True)

        return features.detach().cpu().numpy().astype(np.float32)[0]

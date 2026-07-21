"""SelfMAD++ model backend with lazy heavyweight imports."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Protocol

import numpy as np
from PIL import Image

from .constants import IMAGE_SIZE


class ScoreBackend(Protocol):
    def load(self) -> None: ...

    def score(self, image_rgb: np.ndarray) -> float: ...


class SelfMADBackend:
    def __init__(self, upstream_root: Path, checkpoint_path: Path):
        self.upstream_root = upstream_root.resolve()
        self.checkpoint_path = checkpoint_path.resolve()
        self._model = None
        self._transform = None
        self._torch = None

    def load(self) -> None:
        if self._model is not None:
            return
        try:
            import torch
            from torchvision import transforms
        except ImportError as exc:  # pragma: no cover - model environment only
            raise RuntimeError(
                "Install the CUDA model dependencies before loading SelfMAD++."
            ) from exc

        if not torch.cuda.is_available():
            raise RuntimeError("SelfMAD++ requires a CUDA GPU in this reference service.")
        if torch.cuda.device_count() != 1:
            raise RuntimeError(
                "SelfMAD++ must see exactly one CUDA device per service process; "
                "set CUDA_VISIBLE_DEVICES to one GPU."
            )

        root = str(self.upstream_root)
        if root not in sys.path:
            sys.path.insert(0, root)
        try:
            from model.detector import Detector
        except ImportError as exc:  # pragma: no cover - model environment only
            raise RuntimeError(f"Cannot import pinned SelfMAD++ from {root}.") from exc

        state = torch.load(self.checkpoint_path, map_location="cpu")
        model_type = state.get("model_type", "SelfMAD++")
        if model_type != "SelfMAD++":
            raise RuntimeError(f"Expected a SelfMAD++ checkpoint, found {model_type!r}.")
        model = Detector(model=model_type)
        model.load_state_dict(state["model"], strict=False)
        model.eval()

        self._model = model
        self._transform = transforms.Compose(
            [transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)), transforms.ToTensor()]
        )
        self._torch = torch
        torch.backends.cudnn.benchmark = True

    def score(self, image_rgb: np.ndarray) -> float:
        self.load()
        assert self._model is not None
        assert self._transform is not None
        assert self._torch is not None
        tensor = self._transform(Image.fromarray(image_rgb)).unsqueeze(0).to("cuda")
        with self._torch.inference_mode():
            output = self._model(tensor)
            if isinstance(output, tuple):
                output = output[0]
            return float(output.softmax(1)[0, 1].detach().cpu())

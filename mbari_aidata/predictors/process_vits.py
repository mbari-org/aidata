# mbari_aidata, Apache-2.0 license
# Filename: predictors/process_vits.py
# Description: Process images with a vision backbone, including BackboneClassifier fine-tunes, and store or search embeddings in Redis
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Tuple

import numpy as np
import redis
import torch
from PIL import Image
from transformers import AutoConfig, AutoImageProcessor, AutoModel  # type: ignore

from mbari_aidata.logger import info
from mbari_aidata.predictors.vector_similarity import VectorSimilarity


def _is_backbone_classifier(config: dict) -> bool:
    """True for a fine-tune saved as a plain classification wrapper, not an HF architecture.

    DINOv3 has no AutoModelForImageClassification class, so those runs save a
    BackboneClassifier: config.json says model_type "backbone_classifier" and the
    weights are stored under a "backbone." prefix. AutoModel cannot resolve that type.
    """
    if config.get("model_type") == "backbone_classifier":
        return True
    return "BackboneClassifier" in (config.get("architectures") or [])


def _read_state_dict(model_dir: str) -> dict:
    safe = os.path.join(model_dir, "model.safetensors")
    binary = os.path.join(model_dir, "pytorch_model.bin")
    if os.path.isfile(safe):
        from safetensors.torch import load_file

        return load_file(safe)
    if os.path.isfile(binary):
        return torch.load(binary, map_location="cpu", weights_only=True)
    raise ValueError(f"No model.safetensors or pytorch_model.bin in {model_dir}")


def _align_module_prefixes(state: dict, expected: set) -> dict:
    """Rename saved keys that differ from the model's keys only by a leading module path.

    Transformers versions nest modules differently, e.g. DINOv3 layers are "layer.N" in 4.x
    and "model.layer.N" in 5.x. from_pretrained renames these itself; load_state_dict does not.
    A key is renamed only when exactly one unclaimed expected key matches it.
    """
    unexpected = [k for k in state if k not in expected]
    unclaimed = expected - set(state)
    if not unexpected or not unclaimed:
        return state

    renamed = {}
    for key in unexpected:
        candidates = [m for m in unclaimed if m.endswith("." + key) or key.endswith("." + m)]
        if len(candidates) == 1:
            renamed[key] = candidates[0]
            unclaimed.discard(candidates[0])

    if renamed:
        info(f"Renamed {len(renamed)} backbone weight keys to match the installed transformers module layout")
    return {renamed.get(k, k): v for k, v in state.items()}


def _load_backbone_classifier(model_dir: str, config: dict):
    """Rebuild the fine-tuned backbone and drop the classification head.

    The head is unused here: embeddings are the backbone CLS token. Leaving the
    wrapper's model_type in place makes AutoModel raise, and loading the state dict
    without stripping the "backbone." prefix would keep randomly initialized weights.
    """
    backbone_config = config.get("backbone_config")
    if backbone_config:
        backbone_config = dict(backbone_config)
        model_type = backbone_config.pop("model_type", None)
        if not model_type:
            raise ValueError(f"backbone_config in {model_dir}/config.json has no model_type")
        model = AutoModel.from_config(AutoConfig.for_model(model_type, **backbone_config))
        info(f"Rebuilt a {model_type} backbone from {model_dir}")
    elif config.get("base_model"):
        model = AutoModel.from_pretrained(config["base_model"])
        info(f"Rebuilt the backbone from {config['base_model']}")
    else:
        raise ValueError(
            f"{model_dir}/config.json has neither backbone_config nor base_model, so the architecture cannot be reconstructed."
        )

    state = _read_state_dict(model_dir)
    backbone_state = {}
    foreign = []
    for key, value in state.items():
        if key.startswith("backbone."):
            backbone_state[key[len("backbone.") :]] = value
        elif key.startswith(("classifier.", "dropout.")):
            continue
        else:
            foreign.append(key)

    if not backbone_state:
        raise ValueError(
            f"No backbone weights in {model_dir}; keys start with {sorted({k.split('.')[0] for k in state})}"
        )
    if foreign:
        raise ValueError(f"Unexpected weight keys in {model_dir}: {foreign[:8]}")

    backbone_state = _align_module_prefixes(backbone_state, set(model.state_dict()))
    missing, unexpected = model.load_state_dict(backbone_state, strict=False)
    if missing or unexpected:
        raise ValueError(
            f"Backbone weights in {model_dir} do not match the architecture in backbone_config "
            f"(missing={len(missing)}, unexpected={len(unexpected)})."
        )
    return model


def load_vision_model(model_name: str):
    """Load a vision backbone, including BackboneClassifier fine-tunes AutoModel cannot open."""
    config_path = os.path.join(model_name, "config.json")
    if os.path.isfile(config_path):
        with open(config_path, encoding="utf-8") as f:
            config = json.load(f)
        if _is_backbone_classifier(config):
            info(f"{model_name} is a BackboneClassifier save; loading its backbone and dropping the head")
            model = _load_backbone_classifier(model_name, config)
            # Exemplar vectors are tagged with this path. from_config leaves it empty.
            model.config._name_or_path = model_name
            return model
    return AutoModel.from_pretrained(model_name)


class ViTWrapper:
    DEFAULT_MODEL_NAME = "google/vit-base-patch16-224"

    def __init__(self, r: redis.Redis,
                 device: str = "cpu",
                 model_name: str = DEFAULT_MODEL_NAME,
                 reset: bool = False,
                 batch_size: int = 32):
        self.r = r
        self.batch_size = batch_size
        self.processor = AutoImageProcessor.from_pretrained(model_name)
        self.model = load_vision_model(model_name)
        self.vs = VectorSimilarity(r, vector_dimensions=self.vector_dimensions, reset=reset)

        # Load the model and processor
        if 'cuda' in device and torch.cuda.is_available():
            device_num = int(device.split(":")[-1])
            info(f"Using GPU device {device_num}")
            torch.cuda.set_device(device_num)
            self.device = "cuda"
            self.model.to("cuda")
        else:
            self.device = "cpu"

    @property
    def model_name(self) -> str:
        return self.model.config._name_or_path

    @property
    def vector_dimensions(self) -> int:
        return self.model.config.hidden_size

    def preprocess_pil_images(self, images: List[Image.Image]) -> torch.Tensor:
        """Preprocess a list of PIL images"""
        inputs = self.processor(images=images, return_tensors="pt").to(self.device)
        return inputs

    def preprocess_images(self, image_paths: List[str]) -> dict:
        """Load and preprocess images in parallel with efficient batching"""
        info(f"Preprocessing {len(image_paths)} images")

        with ThreadPoolExecutor(max_workers=min(os.cpu_count(), len(image_paths))) as executor:
            future_to_idx = {
                executor.submit(self._load_image_resized, path): idx
                for idx, path in enumerate(image_paths)
            }

            # Preserve order
            results = [None] * len(image_paths)
            for future in as_completed(future_to_idx):
                idx = future_to_idx[future]
                try:
                    results[idx] = future.result()
                except Exception as e:
                    info(f"Failed to load {image_paths[idx]}: {e}")

        images = [img for img in results if img is not None]

        with torch.no_grad():
            inputs = self.processor(images=images, return_tensors="pt").to(self.device)

        # Release PIL images immediately
        del images

        return inputs

    def get_image_embeddings(self, inputs: torch.Tensor):
        """get embeddings for a batch of images"""
        with torch.no_grad():
            embeddings = self.model(**inputs)
        batch_embeddings = embeddings.last_hidden_state[:, 0, :].cpu().numpy()
        return np.array(batch_embeddings)

    def load(self, image_paths: List[str], class_names: List[str]):
        """Load and preprocess batch of images and add to the vector similarity index"""
        info(f"Loading {len(image_paths)} images")
        unique_class_names = list(set(class_names))
        info(f"Found {len(image_paths)} images to load")

        for i in range(0, len(image_paths), self.batch_size):
            batch = image_paths[i: i + self.batch_size]
            inputs = self.preprocess_images(batch)
            embeddings = self.get_image_embeddings(inputs)

            # Explicitly free GPU memory after each batch
            del inputs
            if self.device == "cuda":
                torch.cuda.empty_cache()

            for j, emb in enumerate(embeddings):
                emb = emb.astype(np.float32)
                assert emb.shape[0] == self.model.config.hidden_size
                self.vs.add_vector(doc_id=class_names[i + j], vector=emb.tobytes(), tag=self.model_name)

            del embeddings

        info(f"Finished processing {len(image_paths)} images for {unique_class_names}")

    def _load_image_resized(self, path: str, target_size: Tuple[int, int] = (224, 224)) -> Image.Image:
        """Load and resize image in one step for better memory efficiency"""
        try:
            with Image.open(path) as img:
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                if img.size != target_size:
                    img = img.resize(target_size, Image.Resampling.LANCZOS)
                return img.copy()  # copy so the file handle can close
        except Exception:
            return None

    def predict(self, image_paths: List[str], top_n: int = 1) -> tuple[
        list[list[str]], list[list[float]], list[list[str]]]:
        """Search using KNN for embeddings for a batch of images"""
        predictions = []
        scores = []
        ids = []

        info(f"Found {len(image_paths)} images to predict")
        for i in range(0, len(image_paths), self.batch_size):
            batch = image_paths[i: i + self.batch_size]
            images, _ = self.preprocess_images(batch)
            embeddings = self.get_image_embeddings(images)
            for j, emb in enumerate(embeddings):
                r = self.vs.search_vector(emb.tobytes(), top_n=top_n)
                # Data is doc:label:id - split it into parts
                data = [x["id"].split(":") for x in r]
                for d in data:
                    if len(d) != 3:
                        continue
                    predictions.append(d[1])
                    ids.append(d[2])
                # Separate out the scores for each prediction - this is used later for voting
                scores.append([x["score"] for x in r])

        return predictions, scores, ids

    def get_ids(self):
        """Get all the ids in the index"""
        all_keys = self.vs.get_all_keys()
        # Data is formatted <doc:label:id>, e.g. doc:Otter:12467, doc:Otter:12467, etc.
        classes = []
        ids = []
        for i, key in enumerate(all_keys):
            str = key.decode("utf-8").split(":")
            if len(str) == 3:
                classes.append(str[1])
                ids.append(str[2])
        return classes, ids

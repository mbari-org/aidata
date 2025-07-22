# mbari_aidata, Apache-2.0 license
# Filename: predictors/process_vits.py
# Description: Process images with Vision Transformer (ViT) model and store/search in Redis
import re

import numpy as np
import redis
import torch
from PIL import Image
from transformers import AutoModel, AutoImageProcessor  # type: ignore
from typing import List

from mbari_aidata.logger import info
from mbari_aidata.predictors.vector_similarity import VectorSimilarity


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
        self.model = AutoModel.from_pretrained(model_name)
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

    def preprocess_images(self, image_paths: List[str]):
        info(f"Preprocessing {len(image_paths)} images")
        images = [Image.open(image_path).convert("RGB") for image_path in image_paths]
        inputs = self.processor(images=images, return_tensors="pt").to(self.device)
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
            images = self.preprocess_images(batch)
            embeddings = self.get_image_embeddings(images)
            for j, emb in enumerate(embeddings):
                # make sure the array matches the vector dimensions and type float32 otherwise indexing will fail
                emb = emb.astype(np.float32)
                assert emb.shape[0] == self.model.config.hidden_size
                self.vs.add_vector(doc_id=class_names[i + j], vector=emb.tobytes(), tag=self.model_name)

        info(f"Finished processing {len(image_paths)} images for {unique_class_names}")

    def predict(self, image_paths: List[str], top_n: int = 1) -> tuple[
        list[list[str]], list[list[float]], list[list[str]]]:
        """Search using KNN for embeddings for a batch of images"""
        predictions = []
        scores = []
        ids = []

        info(f"Found {len(image_paths)} images to predict")
        for i in range(0, len(image_paths), self.batch_size):
            batch = image_paths[i: i + self.batch_size]
            images = self.preprocess_images(batch)
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

# aidata, Apache-2.0 license
# Filename: predictors/process_vits.py
# Description: Process images with Vision Transformer (ViT) model and store/search in Redis
from pathlib import Path

import numpy as np
import redis
import torch
from PIL import Image
from transformers import ViTImageProcessor, ViTModel  # type: ignore
from typing import List

from aidata.logger import info
from aidata.predictors.vector_similarity import VectorSimilarity


class ViTWrapper:
    MODEL_NAME = "google/vit-base-patch16-224"
    VECTOR_DIMENSIONS = 768

    def __init__(self, r: redis.Redis, device: str = "cpu", reset: bool = False, batch_size: int = 32):
        self.r = r
        self.batch_size = batch_size
        self.vs = VectorSimilarity(r, vector_dimensions=self.VECTOR_DIMENSIONS, reset=reset)

        self.model = ViTModel.from_pretrained(self.MODEL_NAME)
        self.processor = ViTImageProcessor.from_pretrained(self.MODEL_NAME)

        # Load the model and processor
        if 'cuda' in device and torch.cuda.is_available():
            device_num = int(device.split(":")[-1])
            torch.cuda.set_device(device_num)
            self.device = "gpu"
            self.model.to("cuda")
        else:
            self.device = "cpu"

    @property
    def model_name(self) -> str:
        return self.MODEL_NAME

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
            batch = image_paths[i : i + self.batch_size]
            images = self.preprocess_images(batch)
            embeddings = self.get_image_embeddings(images)
            for j, emb in enumerate(embeddings):
                self.vs.add_vector(doc_id=class_names[i + j], vector=emb.tobytes(), tag=self.MODEL_NAME)

        info(f"Finished processing {len(image_paths)} images for {unique_class_names}")

    def predict(self, image_paths: List[str], top_n: int = 1) -> tuple[list[list[str]], list[list[float]]]:
        """Search using KNN for embeddings for a batch of images"""
        predictions = []
        scores = []

        info(f"Found {len(image_paths)} images to predict")
        for i in range(0, len(image_paths), self.batch_size):
            batch = image_paths[i : i + self.batch_size]
            images = self.preprocess_images(batch)
            embeddings = self.get_image_embeddings(images)
            for j, emb in enumerate(embeddings):
                r = self.vs.search_vector(emb.tobytes(), top_n=top_n)
                # Only grab the top_n class names, not the scores or other metadata
                r_class_cluster = [x["id"].split(":")[-1] for x in r]
                r_class = [x.split("_")[0] for x in r_class_cluster]
                predictions.append(r_class)
                # Separate out the scores for each prediction - this is used later for voting
                scores.append([x["score"] for x in r])

        return predictions, scores

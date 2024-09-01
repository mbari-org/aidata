# aidata, Apache-2.0 license
# Filename: predictors/process_vits.py
# Description: Process images with Vision Transformer (ViT) model and store/search in Redis
import re

import numpy as np
import redis
import torch
from PIL import Image
from transformers import ViTImageProcessor, ViTModel  # type: ignore
from typing import List

from aidata.logger import info
from aidata.predictors.vector_similarity import VectorSimilarity

def extract_name(input_str):
    match = re.match(r"^(.*?)(?=_[0-9]+)", input_str)
    return match.group(1) if match else None

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
            info(f"Using GPU device {device_num}")
            torch.cuda.set_device(device_num)
            self.device = "cuda"
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
                # make sure the array matches the vector dimensions and type float32 otherwise indexing will fail
                emb = emb.astype(np.float32)
                assert emb.shape[0] == self.VECTOR_DIMENSIONS
                self.vs.add_vector(doc_id=class_names[i + j], vector=emb.tobytes(), tag=self.MODEL_NAME)

        info(f"Finished processing {len(image_paths)} images for {unique_class_names}")

    def predict(self, image_paths: List[str], top_n: int = 1) -> tuple[list[list[str]], list[list[float]], list[list[str]]]:
        """Search using KNN for embeddings for a batch of images"""
        predictions = []
        scores = []
        ids = []

        info(f"Found {len(image_paths)} images to predict")
        for i in range(0, len(image_paths), self.batch_size):
            batch = image_paths[i : i + self.batch_size]
            images = self.preprocess_images(batch)
            embeddings = self.get_image_embeddings(images)
            for j, emb in enumerate(embeddings):
                r = self.vs.search_vector(emb.tobytes(), top_n=top_n)
                # Only grab the top_n class names, not the scores or other metadata
                r_class_cluster = [x["id"].split(":")[-1] for x in r]
                # The class name is everything before the last underscore
                r_class = [extract_name(x) for x in r_class_cluster]
                predictions.append(r_class)
                # The database id is everything after the class name, e.g. Otter_12467
                ids.append(r_class_cluster)
                # Separate out the scores for each prediction - this is used later for voting
                scores.append([x["score"] for x in r])

        return predictions, scores, ids

    def get_ids(self):
        """Get all the ids in the index"""
        all_keys = self.vs.get_all_keys()
        # Class names are indexed, e.g. doc:Otter_12467, doc:Otter_12467, etc.
        classes = []
        ids = []
        for i, key in enumerate(all_keys):
            # Name is everything before the first underscore
            str  = key.decode("utf-8").split("doc:")
            classname, id = str[1].split("_")
            classes.append(classname)
            ids.append(int(id))

        return classes, ids
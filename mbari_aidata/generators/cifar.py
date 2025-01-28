# mbari_aidata, Apache-2.0 license
# Filename: generators/cifar.py
# Description: Creates a CIFAR formatted dataset from a list of media and localizations

import multiprocessing
import tempfile
from typing import List

import numpy as np
from pathlib import Path
from tqdm import tqdm

import tator  # type: ignore

from mbari_aidata.logger import err, info
from PIL import Image


def create_cifar_dataset(
    size: int, data_path: Path, media_lookup_by_id, localizations_by_media: dict, class_names: List[str]
) -> bool:
    """
    Create CIFAR formatted data from a list of media and localizations
    :param size: Size to resize the images to, e.g. 32 for 32x32, 224 for 224x224
    :param data_path: Path to save the data
    :param media_lookup_by_id: Media id to media path lookup
    :param localizations_by_media: Dictionary of localizations by media id
    :param class_names: List of class names
    :return: True if the dataset was created successfully, False otherwise
    """
    images = []
    labels = []

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)

            # Crop the images in parallel using multiprocessing to speed up the processing
            num_processes = min(multiprocessing.cpu_count(), len(media_lookup_by_id))
            info(f"Using {num_processes} processes to crop images...")
            with multiprocessing.Pool(num_processes) as pool:
                args = [
                    [size, temp_path, Path(media_lookup_by_id[media_id]), localizations]
                    for media_id, localizations in localizations_by_media.items()
                ]
                pool.starmap(crop, args)
                pool.close()

            # Read in the images and labels from a temporary directory
            info("Loading images...")
            for npy in tqdm(temp_path.glob("*.npy"), desc="Loading images", unit="iteration"):  # type: ignore
                images.append(np.load(npy.as_posix()).astype("int32"))

                # label name is the last part of the filename after the -
                label_name = npy.stem.split("-")[-1]
                labels.append([int(class_names.index(label_name))])

            # Save the data
            info(f"Saving data to {data_path} ...")
            image_path = data_path / "images.npy"
            label_path = data_path / "labels.npy"
            if image_path.exists():
                image_path.unlink()
            if label_path.exists():
                label_path.unlink()
            np.save(data_path / "images.npy", images)
            np.save(data_path / "labels.npy", labels)
    except Exception as e:
        err(f"Error creating CIFAR dataset: {e}")
        return False

    return True


def crop(size: int, temp_path: Path, image_path: Path, localizations:dict) -> bool:
    """
    Crop the image for a localization
    :param size: Size to resize the image to, e.g. 32 for 32x32, 224 for 224x224
    :param temp_path: Path to the temporary directory
    :param image_path: Path to the image
    :param localizations: Bounding box localization
    :return: True if the image was cropped successfully, False otherwise
    """
    try:
        image_size = (size, size)

        # Get the image
        image = Image.open(image_path)

        image_width, image_height = image.size

        for i, l in enumerate(localizations):
            x1 = int(image_width * l.x)
            y1 = int(image_height * l.y)
            x2 = int(image_width * (l.x + l.width))
            y2 = int(image_height * (l.y + l.height))

            width = x2 - x1
            height = y2 - y1
            shorter_side = min(height, width)
            longer_side = max(height, width)
            delta = abs(longer_side - shorter_side)

            # Divide the difference by 2 to determine how much padding is needed on each side
            padding = delta // 2

            # Add the padding to the shorter side of the image
            if width == shorter_side:
                x1 -= padding
                x2 += padding
            else:
                y1 -= padding
                y2 += padding

            # Crop the image
            img = Image.open(image_path)
            cropped_image = img.crop((x1, y1, x2, y2))

            # Resize the image
            resized_image = cropped_image.resize(image_size, resample=Image.LANCZOS)

            # Convert to numpy array
            image_array = np.asarray(resized_image)

            # Save the image and label to the temporary directory as npy files
            np.save(temp_path / f"{image_path.stem}-image-{l.attributes['Label']}.npy", image_array)

        return True
    except Exception as e:
        err(f"Error processing {image_path}: {e}. Skipping...")
        return False
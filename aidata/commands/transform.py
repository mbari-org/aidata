# aidata, Apache-2.0 license
# Filename: commands/transform.py
# Description: Transform a downloaded dataset for training detection or classification models

from pathlib import Path

import albumentations as albu
import click
import cv2
from tqdm import tqdm
import shutil

from aidata.generators.utils import parse_voc_xml
from aidata.logger import create_logger_file, info, exception
from pascal_voc_writer import Writer  # type: ignore

# Default values
# The base directory is the same directory as this file
DEFAULT_BASE_DIR = Path.home() / "aidata" / "datasets"


@click.command(name="voc", help="Transform a downloaded VOC dataset for training detection models")
@click.option(
    "--base-path",
    default=DEFAULT_BASE_DIR,
    type=Path,
    help=f"Path to the base directory to save all data to. Defaults to {DEFAULT_BASE_DIR}",
)
@click.option("--crop-size", default=640, help="Size of image crop from original.")
@click.option("--crop-overlap", default=0.5, help="Overlap of image crop from original.")
@click.option(
    "--min-area",
    default=100,
    help="Minimum area of a bounding box in pixels. If the area of a bounding box after augmentation becomes "
         "smaller than min_area, it will be dropped.",
)
@click.option(
    "--min-visibility",
    default=0.5,
    help="Minimum visibility of a bounding box between 0-1.  If the ratio of the bounding box area after augmentation  "
         "to the area of the bounding box before augmentation becomes  smaller than min_visibility, it will be dropped.",
)
@click.option("--max-images", type=int, default=-1, help="Only load up to max-images. Useful for testing. "
                                                         "Default is to load all images")
def transform(base_path: str, crop_size: int, crop_overlap: float, min_area: int, min_visibility: float, max_images: int):
    """Transform a downloaded dataset for training detection models"""
    try:
        create_logger_file("transform")
        info(f"Transforming dataset at {base_path} with crop size {crop_size} and overlap {crop_overlap} and min area {min_area}"
             f" and min visibility {min_visibility} and max images {max_images}")

        # Check if the base path exists and a voc dataset exists:
        if not Path(base_path).exists():
            exception(f"Base path {base_path} does not exist.")
            return

        # Check if the base path has a VOC dataset - this should
        # be a directory with the following structure:
        # base_path
        # ├── images
        # │   ├── image1.png
        # │   ├── image2.png
        # ├── voc
        # │   ├── image1.xml
        # │   ├── image2.xml
        if not Path(base_path / "voc").exists():
            exception(f"VOC dataset not found in {base_path}")
            return

        if not Path(base_path / "images").exists():
            exception(f"Images directory not found in {base_path}")
            return

        step_size = int(crop_size * (1 - crop_overlap))

        allowed_extensions = [".png", ".jpg", ".jpeg", ".JPEG", ".JPG", ".PNG"]

        image_paths = [image_path for image_path in Path(base_path / "images").glob("*") if image_path.suffix in allowed_extensions]
        if len(image_paths) == 0:
            exception(f"No images found in {base_path / 'images'}")
            return

        if max_images > 0:
            image_paths = image_paths[:max_images]

        output_base_path = base_path / "transformed"
        output_base_path_xml = output_base_path / "voc"
        output_base_path_images = output_base_path / "images"
        if output_base_path.exists():
            info(f"Removing existing transformed dataset at {output_base_path}")
            shutil.rmtree(output_base_path.as_posix())
        output_base_path.mkdir(exist_ok=True)
        output_base_path_xml.mkdir(exist_ok=True, parents=True)
        output_base_path_images.mkdir(exist_ok=True, parents=True)
        num_transformed_labels = 0
        label_cnt = {}
        label_cnt_transformed = {}
        num_images = 0
        for image_path in tqdm(image_paths, desc="transforming", unit="iteration"):
            image = cv2.imread(str(image_path))
            if image is None:
                exception(f"Could not read image {image_path}")
                continue
            num_images += 1

            xml_path = base_path / "voc" / (image_path.name + ".xml")
            if not xml_path.exists():
                exception(f"Could not find annotation file {xml_path}")
                continue

            # Load the annotations from the VOC XML file
            boxes, labels, poses, ids = parse_voc_xml(xml_path)

            # Count the number of labels
            for label in labels:
                if label not in label_cnt:
                    label_cnt[label] = 0
                label_cnt[label] += 1

            # Get image dimensions for cropping
            image_height, image_width, _ = image.shape

            # Iterate over the image to generate overlapping crops
            i = 0  # counter for the cropped images
            for y in range(0, image_height - crop_size + 1, step_size):
                for x in range(0, image_width - crop_size + 1, step_size):
                    crop = albu.Crop(x_min=x, y_min=y, x_max=x + crop_size, y_max=y + crop_size)

                    # Define the augmentation pipeline
                    transform = albu.Compose(
                        [
                            crop,
                            albu.LongestMaxSize(max_size=crop_size),
                        ],
                        bbox_params=albu.BboxParams(format="pascal_voc", min_visibility=min_visibility, min_area=min_area, label_fields=["labels", "ids"]),
                    )
                    # Apply the transformation
                    transformed = transform(image=image, bboxes=boxes, labels=labels, ids=ids)

                    # Only keep the data if the cropped image contains at least one bounding box
                    if len(transformed["bboxes"]) > 0:
                        num_transformed_labels += len(transformed["bboxes"])
                        image_path_final = output_base_path_images / f"{image_path.stem}_t_{i}{image_path.suffix}"
                        voc_xml_path = output_base_path_xml / f"{image_path_final.stem}.xml"
                        writer = Writer(voc_xml_path.as_posix(), crop_size, crop_size)

                        # Store the cropped image and adjusted bounding boxes
                        for bbox, label, id in zip(transformed["bboxes"], transformed["labels"], transformed["ids"]):
                            if label not in label_cnt_transformed:
                                label_cnt_transformed[label] = 0
                            label_cnt_transformed[label] += 1
                            x1, y1, x2, y2 = map(int, bbox)
                            writer.addObject(label, x1, y1, x2, y2, pose=str(id))
                            # To visualize the bounding boxes uncomment the following line
                            # cv2.rectangle(transformed['image'], (x1, y1), (x2, y2), (255, 0, 0), 2)

                        # Write the file
                        writer.save(voc_xml_path.as_posix())

                        # Replace the xml tag pose with id
                        with open(voc_xml_path, "r") as file:
                            filedata = file.read()
                        filedata = filedata.replace("pose", "id")
                        with open(voc_xml_path, "w") as file:
                            file.write(filedata)

                        # Save the image
                        cv2.imwrite(image_path_final.as_posix(), transformed["image"])

                        i += 1

        info(f"transformed dataset saved to {output_base_path}")
        num_transformed_images = len(list(output_base_path_images.glob("*")))
        info(f"Input images: {num_images}; transformed images: {num_transformed_images}")
        info(f"Input labels: {label_cnt}; transformed labels: {label_cnt_transformed}")

    except Exception as e:
        exception(f"Error: {e}")
        raise e


if __name__ == "__main__":
    base_path = Path(__file__).parent.parent.parent / "Baseline"
    transform(base_path=base_path, crop_size=640, crop_overlap=0.5, min_area=100, min_visibility=0.5, max_images=-1)

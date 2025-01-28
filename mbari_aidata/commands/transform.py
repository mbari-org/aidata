# mbari_aidata, Apache-2.0 license
# Filename: commands/transform.py
# Description: Transform a downloaded dataset for training detection or classification models

from pathlib import Path

import albumentations as albu
import click
import cv2
from tqdm import tqdm
import shutil

from mbari_aidata.generators.utils import parse_voc_xml
from mbari_aidata.logger import create_logger_file, info, exception, warn
from pascal_voc_writer import Writer  # type: ignore

# Default values
# The base directory is the same directory as this file
DEFAULT_BASE_DIR = Path.home() / "mbari_aidata" / "datasets"


@click.command(name="voc", help="Transform a downloaded VOC dataset for training detection models")
@click.option(
    "--base-path",
    default=DEFAULT_BASE_DIR,
    type=Path,
    help=f"Path to the base directory to save all data to. Defaults to {DEFAULT_BASE_DIR}",
)
@click.option("--crop-size", type=int, help="Size of image crop from original.")
@click.option("--crop-overlap", type=float, default=0.5, help="Overlap of image crop from original.")
@click.option("--resize", type=int, help="Resize the image to a specific size, e.g. 640x480. "
                               "            Don't resize if not specified. Done in addition to crop.")
@click.option(
    "--min-area",
    default=100,
    help="Minimum area of a bounding box in pixels. If the area of a bounding box after augmentation becomes "
         "smaller than min_area, it will be dropped.",
)
@click.option(
    "--min-dim",
    default=20,
    help="Minimum dimension of a bounding box in pixels. If the area of a bounding box after augmentation becomes "
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
def transform(base_path: str, resize: int, crop_size: int, crop_overlap: float, min_area: int, min_dim: int,
              min_visibility: float, max_images: int):
    """Transform a downloaded dataset for training detection models"""
    try:
        create_logger_file("transform")
        info(
            f"Transforming dataset at {base_path} with crop size {crop_size} and overlap {crop_overlap} and min area {min_area}"
            f" and min visibility {min_visibility} and max images {max_images}")

        if resize:
            info(f"Resizing images to {resize}")

        if crop_size:
            info(f"Cropping images to {crop_size} with overlap {crop_overlap}")
            step_size = int(crop_size * (1 - crop_overlap))

        # Need to specify either crop_size or resize or both
        if not crop_size and not resize:
            exception("Either crop-size or resize must be specified")
            return

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

        allowed_extensions = [".png", ".jpg", ".jpeg", ".JPEG", ".JPG", ".PNG"]

        image_paths = [image_path for image_path in Path(base_path / "images").glob("*") if
                       image_path.suffix in allowed_extensions]
        if len(image_paths) == 0:
            exception(f"No images found in {base_path / 'images'}")
            return

        if max_images > 0:
            image_paths = image_paths[:max_images]

        # A utility function to remove the bounding boxes that are too small
        def remove_small_boxes(transformed_data, transformed_xml_path) -> dict:
            boxes_ = transformed_data["bboxes"]
            labels_ = transformed_data["labels"]
            ids_ = transformed_data["ids"]
            new_boxes, new_labels, new_ids = [], [], []
            for b, l, myid in zip(boxes_, labels_, ids_):
                x1, y1, x2, y2 = map(int, b)
                if x2 - x1 < min_dim or y2 - y1 < min_dim:
                    info(f"Removing box {b} for {transformed_xml_path}")
                    continue
                new_boxes.append(b)
                new_labels.append(l)
                new_ids.append(myid)
            transformed_data["bboxes"] = new_boxes
            transformed_data["labels"] = new_labels
            transformed_data["ids"] = new_ids
            return transformed_data

        # A utility function for saving the transformed data
        def save_transformed(transformed_xml_path: Path, width: int, height: int, transformed_data: dict, line_width=2):
            writer = Writer(transformed_xml_path.as_posix(), width, height)

            # Store the cropped image and adjusted bounding boxes
            for l, b, i in zip(transformed_data["labels"], transformed_data["bboxes"], transformed_data["ids"]):
                if l not in label_cnt_transformed:
                    label_cnt_transformed[l] = 0
                label_cnt_transformed[l] += 1
                x1, y1, x2, y2 = map(int, b)
                writer.addObject(l, x1, y1, x2, y2, pose=str(i))
                # To visualize the bounding boxes uncomment the following line
                # cv2.rectangle(transformed['image'], (x1, y1), (x2, y2), (255, 0, 0), 2)

            # Write the file
            writer.save(voc_xml_path.as_posix())

            # Replace the xml tag pose with the database id
            with open(voc_xml_path, "r") as file:
                filedata = file.read()
            filedata = filedata.replace("pose", "id")
            with open(voc_xml_path, "w") as file:
                file.write(filedata)

        # Create the output directories
        output_base_path = base_path / "transformed"
        output_base_path_xml = output_base_path / "voc"
        output_base_path_images = output_base_path / "images"
        if output_base_path.exists():
            info(f"Removing existing transformed dataset at {output_base_path}")
            shutil.rmtree(output_base_path.as_posix())
        output_base_path.mkdir(exist_ok=True)
        output_base_path_xml.mkdir(exist_ok=True, parents=True)
        output_base_path_images.mkdir(exist_ok=True, parents=True)

        # Initialize counters
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

            if resize:
                transform_resize = albu.Compose([
                    albu.Resize(width=resize, height=resize),
                ], bbox_params=albu.BboxParams(format='pascal_voc',
                                               min_area=min_area,
                                               min_visibility=min_visibility,
                                               label_fields=["labels", "ids"]))

                # Save the transformed image with the same name with _r, e.g. image_r.png
                image_path_final = output_base_path_images / f"{image_path.stem}_r{image_path.suffix}"
                voc_xml_path = output_base_path_xml / f"{image_path_final.stem}.xml"

                # Apply the transformation and save
                transformed = transform_resize(image=image, bboxes=boxes, labels=labels, ids=ids)
                if len(transformed['bboxes']) != len(transformed['labels']):
                    warn(f'Transform failed for {voc_xml_path}')
                    continue

                # If the boxes are smaller than min_dim pixels in height or width, remove them
                transformed = remove_small_boxes(transformed, voc_xml_path)

                if len(transformed['bboxes']) == 0:
                    warn(f'No bounding boxes left for {voc_xml_path}')
                    continue

                save_transformed(voc_xml_path, resize, resize, transformed, line_width=10)
                cv2.imwrite(image_path_final.as_posix(), transformed["image"])

            if not crop_size:
                continue

            # Iterate over the image to generate overlapping crops
            i = 0  # counter for indexing the transformed images to give them a unique name
            for y in range(0, image_height - crop_size + 1, step_size):
                for x in range(0, image_width - crop_size + 1, step_size):
                    crop = albu.Crop(x_min=x, y_min=y, x_max=x + crop_size, y_max=y + crop_size)

                    # Define the augmentation pipeline
                    transform = albu.Compose(
                        [
                            crop,
                            albu.LongestMaxSize(max_size=crop_size),
                        ],
                        bbox_params=albu.BboxParams(format="pascal_voc", min_visibility=min_visibility,
                                                    min_area=min_area, label_fields=["labels", "ids"]),
                    )
                    # Apply the transformation
                    transformed = transform(image=image, bboxes=boxes, labels=labels, ids=ids)

                    # Save the transformed image with the same name with _c, e.g. image_c.png
                    image_path_final = output_base_path_images / f"{image_path.stem}_c_{i}{image_path.suffix}"
                    voc_xml_path = output_base_path_xml / f"{image_path_final.stem}.xml"

                    # If the boxes are smaller than min_dim pixels in height or width, remove them
                    transformed = remove_small_boxes(transformed, voc_xml_path)

                    # Only keep the data if the cropped image contains at least one bounding box
                    if len(transformed["bboxes"]) > 0:
                        num_transformed_labels += len(transformed["bboxes"])
                        save_transformed(voc_xml_path, crop_size, crop_size, transformed, line_width=2)
                        cv2.imwrite(image_path_final.as_posix(), transformed["image"])
                        i += 1

        info(f"transformed dataset saved to {output_base_path}")
        num_transformed_images = len(list(output_base_path_images.glob("*")))
        info(f"Input images: {num_images}; transformed images: {num_transformed_images}")
        info(f"Input labels: {label_cnt}; transformed labels: {label_cnt_transformed}")

    except Exception as e:
        exception(f"Error: {e}")
        raise e


@click.command(name="voc-to-yolo", help="Transform a downloaded VOC dataset for training detection models")
@click.option(
    "--base-path",
    default=DEFAULT_BASE_DIR,
    type=Path,
    help=f"Path to the base directory to save all data to. Defaults to {DEFAULT_BASE_DIR}",
)
def voc_to_yolo(base_path: str):
    """Transform a downloaded dataset for training detection models from VOC to YOLO format"""
    try:
        create_logger_file("transform")
        info(f"Transforming dataset at {base_path} from VOC to YOLO format")

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
        # labels.txt
        if not Path(base_path / "voc").exists():
            exception(f"VOC dataset not found in {base_path}")
            return

        if not Path(base_path / "images").exists():
            exception(f"Images directory not found in {base_path}")
            return

        # Create a mapping of label names to label indices, starting from 0 in sorted order from the labels.txt file
        label_map = {}
        with open(base_path.parent / "labels.txt", "r") as file:
            labels = file.read().splitlines()
        labels.sort()
        for i, label in enumerate(labels):
            label_map[label] = i

        # Create the YOLO directory if it does not exist
        # This output will be a directory with the following structure:
        # base_path
        # ├── images
        # │   ├── image1.png
        # │   ├── image2.png
        # ├── labels
        # │   ├── image1.txt
        # │   ├── image2.txt
        # labels.txt
        yolo_path = base_path / "labels"
        yolo_path.mkdir(exist_ok=True)

        for xml_path in Path(base_path / "voc").glob("*.xml"):
            # Load the annotations from the VOC XML file
            boxes, labels, poses, ids = parse_voc_xml(xml_path)

            # Get image dimensions for normalization
            allowed_extensions = [".png", ".jpg", ".jpeg", ".JPEG", ".JPG", ".PNG"]
            for ext in allowed_extensions:
                image_path = base_path / "images" / (xml_path.stem + ext)
                if image_path.exists():
                    break
            image = cv2.imread(str(image_path))
            if image is None:
                exception(f"Could not read image {image_path}")
                continue
            image_height, image_width, _ = image.shape

            # Write the YOLO format file
            yolo_out_path = yolo_path / (xml_path.stem + ".txt")
            with yolo_out_path.open("w") as file:
                for box, label in zip(boxes, labels):
                    x1, y1, x2, y2 = map(int, box)
                    x_center = (x1 + x2) / 2 / image_width
                    y_center = (y1 + y2) / 2 / image_height
                    width = (x2 - x1) / image_width
                    height = (y2 - y1) / image_height
                    # Make sure to bound the x_center + width and
                    # y_center + height to 1 by reducing the width and height
                    if x_center + width > 1:
                        width = 1 - x_center
                    if y_center + height > 1:
                        height = 1 - y_center
                    label_index = label_map[label]
                    file.write(f"{label_index} {x_center} {y_center} {width} {height}\n")

        # Report an error is there are no .txt files generated
        if len(list(yolo_path.glob("*.txt"))) == 0:
            exception(f"No YOLO files generated in {yolo_path}")

    except Exception as e:
        exception(f"Error: {e}")
        raise e


if __name__ == "__main__":
    base_path = Path(__file__).parent.parent.parent / "Baseline"
    transform(base_path=base_path, crop_size=2000, crop_overlap=0.5, min_area=100, min_visibility=0.5, resize=None,
              max_images=-1)

# mbari_aidata, Apache-2.0 license
# Filename: tests/test_transform.py
# Description: Tests for the transform voc command, including negative example support

import os
import tempfile
from pathlib import Path

import cv2
import numpy as np
import pytest
from click.testing import CliRunner

from mbari_aidata.commands.transform import transform
from mbari_aidata.logger import CustomLogger

CustomLogger(output_path=Path.cwd() / "logs", output_prefix=__name__)

IMAGE_SIZE = 100
CROP_SIZE = 50
# With crop_overlap=0.0 and a 100x100 image cropped into 50x50 tiles, this yields a 2x2 grid
# (4 crops per image): one containing the annotated box (positive) and three empty (negative candidates).
CROPS_PER_IMAGE = 4


def setup():
    os.environ["ENVIRONMENT"] = "TESTING"


def _write_voc_xml(xml_path: Path, image_name: str, box=None):
    """Write a minimal VOC XML annotation file, optionally with a single bounding box."""
    objects = ""
    if box is not None:
        xmin, ymin, xmax, ymax = box
        objects = f"""
    <object>
        <name>fish</name>
        <pose>Unspecified</pose>
        <id>1</id>
        <bndbox>
            <xmin>{xmin}</xmin>
            <ymin>{ymin}</ymin>
            <xmax>{xmax}</xmax>
            <ymax>{ymax}</ymax>
        </bndbox>
    </object>"""
    xml_path.write_text(f"""<annotation>
    <filename>{image_name}</filename>
    <size>
        <width>{IMAGE_SIZE}</width>
        <height>{IMAGE_SIZE}</height>
        <depth>3</depth>
    </size>{objects}
</annotation>""")


@pytest.fixture
def voc_dataset():
    """Create a small VOC dataset where every image has exactly one annotated box confined
    to the top-left crop quadrant, so each image yields 1 positive and 3 negative crop candidates."""
    with tempfile.TemporaryDirectory() as tmpdir:
        base_path = Path(tmpdir) / "dataset"
        images_dir = base_path / "images"
        voc_dir = base_path / "voc"
        images_dir.mkdir(parents=True)
        voc_dir.mkdir(parents=True)

        num_images = 10
        for i in range(num_images):
            image_name = f"image_{i:03d}.png"
            image = np.zeros((IMAGE_SIZE, IMAGE_SIZE, 3), dtype=np.uint8)
            cv2.imwrite(str(images_dir / image_name), image)
            # Box fully inside the top-left 50x50 crop quadrant
            _write_voc_xml(voc_dir / f"image_{i:03d}.xml", image_name, box=(5, 5, 25, 25))

        yield base_path, num_images


def test_transform_no_negatives_by_default(voc_dataset):
    """By default (negative-percent=0.0), only annotated crops should be kept."""
    base_path, num_images = voc_dataset

    runner = CliRunner()
    result = runner.invoke(
        transform,
        ["--base-path", str(base_path), "--crop-size", str(CROP_SIZE), "--crop-overlap", "0.0"],
    )

    assert result.exit_code == 0, f"Command should succeed, got: {result.output}"

    transformed_images = list((base_path / "transformed" / "images").glob("*"))
    negatives = [p for p in transformed_images if "_neg" in p.stem]

    assert len(negatives) == 0, "No negative examples should be produced when negative-percent is 0"
    assert len(transformed_images) == num_images, "Only the one positive crop per image should be kept"


def test_transform_negatives_capped_by_percent(voc_dataset):
    """Negative examples should be included, but capped so they never exceed negative-percent of the dataset."""
    base_path, num_images = voc_dataset
    negative_percent = 0.2

    runner = CliRunner()
    result = runner.invoke(
        transform,
        [
            "--base-path", str(base_path),
            "--crop-size", str(CROP_SIZE),
            "--crop-overlap", "0.0",
            "--negative-percent", str(negative_percent),
        ],
    )

    assert result.exit_code == 0, f"Command should succeed, got: {result.output}"

    transformed_images = list((base_path / "transformed" / "images").glob("*"))
    negatives = [p for p in transformed_images if "_neg" in p.stem]
    positives = [p for p in transformed_images if "_neg" not in p.stem]

    assert len(positives) == num_images
    # There are 3 negative candidates per image; make sure some were actually eligible
    assert num_images * (CROPS_PER_IMAGE - 1) > 0

    total = len(positives) + len(negatives)
    assert len(negatives) > 0, "Some negative examples should be kept when negative-percent > 0"
    assert len(negatives) / total <= negative_percent + 1e-9, (
        "Negative examples must not exceed negative-percent of the transformed dataset"
    )

    # Every negative image should have a corresponding VOC XML with no objects
    for neg_image in negatives:
        xml_path = base_path / "transformed" / "voc" / f"{neg_image.stem}.xml"
        assert xml_path.exists()
        assert "<object>" not in xml_path.read_text()


def test_transform_invalid_negative_percent(voc_dataset):
    """negative-percent must be within [0, 1); invalid values should abort before producing any output."""
    base_path, _ = voc_dataset

    runner = CliRunner()
    result = runner.invoke(
        transform,
        [
            "--base-path", str(base_path),
            "--crop-size", str(CROP_SIZE),
            "--negative-percent", "1.5",
        ],
    )

    assert result.exit_code == 0
    assert not (base_path / "transformed").exists(), "No transformed output should be created for an invalid value"

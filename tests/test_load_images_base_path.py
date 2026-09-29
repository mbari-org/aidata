# mbari_aidata, Apache-2.0 license
# Filename: tests/test_load_images_base_path.py
# Description: Tests reference image URL formatting and the load images --base-path option
from pathlib import Path

import click
import pytest

from mbari_aidata.commands.load_images import load_images, reference_image_url


def test_reference_image_url_strips_mount_path():
    """Test that the mount path is removed when building a reference image URL."""
    url = reference_image_url(
        "/data/cfe/images/frame.jpg",
        "http://localhost:8082/tests/",
        Path("/data"),
    )
    assert url == "http://localhost:8082/tests//cfe/images/frame.jpg"


def test_reference_image_url_uses_optional_base_path(tmp_path: Path):
    """Test that --base-path replaces the mount path as the prefix stripped from the URL."""
    image = tmp_path / "images" / "frame.jpg"
    image.parent.mkdir()
    image.touch()

    url = reference_image_url(str(image), "http://localhost:8082/tests/", tmp_path)

    assert url == f"http://localhost:8082/tests//{image.relative_to(tmp_path).as_posix()}"


def test_reference_image_url_leaves_http_paths_unchanged():
    """Test that an image path that is already a URL is not rewritten."""
    original = "http://example.com/frame.jpg"
    assert reference_image_url(original, "http://localhost:8082/tests/", Path("/data")) == original


def test_reference_image_url_rejects_path_outside_base(tmp_path: Path):
    """Test that a media path outside the base path is rejected."""
    with pytest.raises(ValueError, match="not under base path"):
        reference_image_url("/other/frame.jpg", "http://localhost:8082/tests/", tmp_path)


def test_base_path_is_rejected_with_upload():
    """Test that --base-path cannot be combined with --upload."""
    with pytest.raises(click.UsageError, match="--base-path is only valid when --upload is not used"):
        load_images.callback(
            token="token",
            disable_ssl_verify=False,
            config="config.yml",
            dry_run=False,
            input="images",
            section="All Media",
            max_images=-1,
            check_duplicates=False,
            upload=True,
            base_path=Path("/tmp"),
        )

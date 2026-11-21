# mbari_aidata, Apache-2.0 license
# Filename: tests/test_crop_roi_media_cleanup.py
# Description: Tests that --crop-roi keeps full-frame images unless deletion is requested

import shutil
from pathlib import Path
from types import SimpleNamespace

import tator

from mbari_aidata.generators.coco_voc import download

FIXTURE_IMAGE = Path(__file__).parent / "data" / "cfe" / "CFE_ISIIS-010-2024-01-26 10-14-07.102_0835.png"


class FakeMedia:
    """Fake tator.models.Media."""

    def __init__(self, id, name, width=None, height=None, attributes=None, elemental_id="media-elem-1", fps=None):
        self.id = id
        self.name = name
        self.width = width
        self.height = height
        self.attributes = attributes or {}
        self.elemental_id = elemental_id
        self.fps = fps


class FakeLocalization:
    """Fake tator.models.Localization."""

    def __init__(self, id, media, x, y, width, height, attributes, frame=0, elemental_id="loc-elem-1"):
        self.id = id
        self.media = media
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.attributes = attributes
        self.frame = frame
        self.elemental_id = elemental_id

    def to_dict(self):
        return {
            "id": self.id,
            "media": self.media,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "attributes": self.attributes,
            "frame": self.frame,
            "elemental_id": self.elemental_id,
        }


class FakeApi:
    """Fake tator.api with one media item and one localization."""

    def __init__(self, media, loc, version_id=1, version_name="testset"):
        self.media = media
        self.loc = loc
        self.version_id = version_id
        self.version_name = version_name

    def get_version_list(self, project):
        return [SimpleNamespace(id=self.version_id, name=self.version_name)]

    def get_localization_count(self, project, **kwargs):
        return 1

    def get_media_list(self, project, **kwargs):
        if "media_id" in kwargs or "related_attribute" in kwargs or "attribute" in kwargs:
            return [self.media]
        return []

    def get_localization_list(self, project, start, stop, version, **kwargs):
        return [self.loc]


def _run_crop_download(tmp_path, monkeypatch, media_name, delete_full_frames):
    monkeypatch.setattr(tator.models, "Media", FakeMedia)
    monkeypatch.setattr(tator.models, "Localization", FakeLocalization)
    monkeypatch.setattr("mbari_aidata.generators.coco_voc.crop_frame_multi", lambda *_args, **_kwargs: None)

    media = FakeMedia(id=101, name=media_name, width=640, height=480)
    loc = FakeLocalization(
        id=5001,
        media=media.id,
        x=0.1,
        y=0.1,
        width=0.2,
        height=0.2,
        attributes={"Label": "Orcinus Orca"},
    )
    api = FakeApi(media=media, loc=loc)

    output_path = tmp_path / "export"
    media_path = output_path / "media"
    media_path.mkdir(parents=True)
    local_file = media_path / media.name
    if Path(media_name).suffix.lower() == ".png":
        shutil.copy(FIXTURE_IMAGE, local_file)
    else:
        local_file.write_bytes(b"not-a-real-video")

    ok = download(
        api=api,
        project_id=1,
        group=None,
        depth=None,
        section=None,
        version_list=[api.version_name],
        verified=True,
        unverified=False,
        generator=None,
        output_path=output_path,
        labels_list=[],
        concepts_list=[],
        skip_image_download=True,
        voc=False,
        coco=False,
        cifar=False,
        crop_roi=True,
        delete_full_frames=delete_full_frames,
    )
    assert ok
    return local_file


def test_crop_roi_keeps_full_frame_image_by_default(tmp_path, monkeypatch):
    """Test that cropping ROIs leaves the downloaded full-frame image on disk."""
    local_file = _run_crop_download(tmp_path, monkeypatch, FIXTURE_IMAGE.name, delete_full_frames=False)
    assert local_file.exists()


def test_crop_roi_delete_removes_full_frame_image(tmp_path, monkeypatch):
    """Test that delete_full_frames removes the downloaded full-frame image after crops."""
    local_file = _run_crop_download(tmp_path, monkeypatch, FIXTURE_IMAGE.name, delete_full_frames=True)
    assert not local_file.exists()


def test_crop_roi_delete_keeps_source_video(tmp_path, monkeypatch):
    """Test that delete_full_frames leaves source videos in place after ROI crops."""
    local_file = _run_crop_download(tmp_path, monkeypatch, "dive.mp4", delete_full_frames=True)
    assert local_file.exists()

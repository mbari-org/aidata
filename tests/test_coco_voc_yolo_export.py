# mbari_aidata, Apache-2.0 license
# Filename: tests/test_yolo_label_naming.py
# Description: Tests YOLO label export must write
#    NAME.txt for an image NAME.<ext>, not NAME.<ext>.txt.


import shutil
from pathlib import Path
from types import SimpleNamespace

import tator

from mbari_aidata.generators.coco_voc import download

# FIXTURE_IMAGE = Path(__file__).parent / "data" / "uav" / "trinity-2_20250404T173830_Seymour_DSC01963.JPG"
FIXTURE_IMAGE = Path(__file__).parent / "data" / "cfe" / \
    "CFE_ISIIS-010-2024-01-26 10-14-07.102_0835.png"


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


class FakeApi:
    """Fake tator.api."""

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
        if "media_id" in kwargs or "related_attribute" in kwargs:
            return [self.media]
        return []

    def get_localization_list(self, project, start, stop, version, **kwargs):
        return [self.loc]


def _run_download(tmp_path, monkeypatch):
    monkeypatch.setattr(tator.models, "Media", FakeMedia)
    monkeypatch.setattr(tator.models, "Localization", FakeLocalization)

    media = FakeMedia(id=101, name=FIXTURE_IMAGE.name)
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
    output_path.mkdir()
    media_path = output_path / "media"
    media_path.mkdir()
    shutil.copy(FIXTURE_IMAGE, media_path / media.name)  # avoif Tator

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
        skip_image_download=True,  # image already placed above to avoid network call
        voc=False,
        coco=False,
        cifar=False,
        crop_roi=False,
    )
    assert ok
    return output_path, media.name


def test_yolo_label_file_matches_image_stem_not_full_filename(tmp_path, monkeypatch):
    # issue #76
    output_path, image_name = _run_download(tmp_path, monkeypatch)
    label_path = output_path / "labels"

    expected = label_path / f"{Path(image_name).stem}.txt"
    buggy = label_path / f"{image_name}.txt"

    assert expected.exists(), (
        f"Expected YOLO label file {expected.name!r} was not created."
    )
    assert not buggy.exists(), (
        f"Found double-extension label file {buggy.name!r}."
    )

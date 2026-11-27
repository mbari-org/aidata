# mbari_aidata, Apache-2.0 license
# Filename: tests/test_coco_voc_concurrent.py
# Description: Tests that download(concurrent=True) adds every localization sharing a frame with a
#    selected one, ignoring the localization filters, for full-coverage detection datasets.

import shutil
import xml.etree.ElementTree as ET
from pathlib import Path

import tator

from mbari_aidata.generators.coco_voc import download
from test_coco_voc_yolo_export import FIXTURE_IMAGE, FakeApi, FakeLocalization, FakeMedia


class ConcurrentFakeApi(FakeApi):
    """Returns only the filtered localizations unless queried by media_id, which returns everything on that media."""

    def __init__(self, media, filtered_locs, all_locs):
        super().__init__(media=media, loc=None)
        self.filtered_locs = filtered_locs
        self.all_locs = all_locs
        self.media_id_queries = []

    def get_localization_list(self, project, start, stop, version, **kwargs):
        if "media_id" in kwargs:
            self.media_id_queries.append(kwargs)
            assert "attribute" not in kwargs and "attribute_contains" not in kwargs
            locs = [l for l in self.all_locs if l.media in kwargs["media_id"]]
        else:
            locs = self.filtered_locs
        return locs[start:stop]


def _run(tmp_path, monkeypatch, concurrent):
    monkeypatch.setattr(tator.models, "Media", FakeMedia)
    monkeypatch.setattr(tator.models, "Localization", FakeLocalization)

    media = FakeMedia(id=101, name=FIXTURE_IMAGE.name)
    verified_fish = FakeLocalization(5001, media.id, 0.1, 0.1, 0.2, 0.2, {"Label": "Fish", "verified": True})
    unverified_crab = FakeLocalization(5002, media.id, 0.5, 0.5, 0.1, 0.1, {"Label": "Crab", "verified": False})
    other_frame = FakeLocalization(5003, media.id, 0.3, 0.3, 0.1, 0.1, {"Label": "Crab"}, frame=7)
    other_media = FakeLocalization(5004, 999, 0.3, 0.3, 0.1, 0.1, {"Label": "Crab"})
    api = ConcurrentFakeApi(
        media=media,
        filtered_locs=[verified_fish],
        all_locs=[verified_fish, unverified_crab, other_frame, other_media],
    )

    output_path = tmp_path / "export"
    (output_path / "media").mkdir(parents=True)
    shutil.copy(FIXTURE_IMAGE, output_path / "media" / media.name)

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
        labels_list=["Fish"],
        concepts_list=[],
        skip_image_download=True,
        voc=True,
        concurrent_localizations=concurrent,
    )
    assert ok
    xml_path = output_path / "voc" / f"{Path(media.name).stem}.xml"
    names = sorted(obj.find("name").text for obj in ET.parse(xml_path).getroot().iter("object"))
    return api, names, (output_path / "labels.txt").read_text().split()


def test_without_concurrent_only_filtered_localizations(tmp_path, monkeypatch):
    api, names, labels = _run(tmp_path, monkeypatch, concurrent=False)
    assert names == ["Fish"]
    assert labels == ["Fish"]
    assert api.media_id_queries == []


def test_concurrent_adds_same_frame_localizations_only(tmp_path, monkeypatch):
    api, names, labels = _run(tmp_path, monkeypatch, concurrent=True)
    # The unverified Crab on the same frame is added; the frame 7 Crab and the other media's Crab are not.
    assert names == ["Crab", "Fish"]
    assert sorted(labels) == ["Crab", "Fish"]
    assert api.media_id_queries and api.media_id_queries[0]["media_id"] == [101]

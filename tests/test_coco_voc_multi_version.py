# mbari_aidata, Apache-2.0 license
# Filename: tests/test_coco_voc_multi_version.py
# Description: Tests that the per-frame NMS run for multi-version downloads keeps the localizations of every
#    frame, not only the last one.

from pathlib import Path
from types import SimpleNamespace

import tator

from mbari_aidata.generators.coco_voc import download
from test_coco_voc_yolo_export import FakeApi, FakeLocalization, FakeMedia


class MultiVersionFakeApi(FakeApi):
    def __init__(self, media, locs):
        super().__init__(media=media, loc=None)
        self.locs = locs

    def get_version_list(self, project):
        return [SimpleNamespace(id=1, name="v1"), SimpleNamespace(id=2, name="v2")]

    def get_media_list(self, project, **kwargs):
        return [self.media]

    def get_localization_list(self, project, start, stop, version, **kwargs):
        return self.locs[start:stop]


def test_multi_version_nms_keeps_all_frames(tmp_path, monkeypatch):
    monkeypatch.setattr(tator.models, "Media", FakeMedia)
    monkeypatch.setattr(tator.models, "Localization", FakeLocalization)

    media = FakeMedia(id=101, name="dive.mp4", width=1920, height=1080, fps=30)
    locs = [
        # Frame 0: the same Fish in both versions, which NMS should merge into one box
        FakeLocalization(1, media.id, 0.1, 0.1, 0.2, 0.2, {"Label": "Fish", "score": 0.9}, frame=0),
        FakeLocalization(2, media.id, 0.1, 0.1, 0.2, 0.2, {"Label": "Fish", "score": 0.8}, frame=0),
        # Frame 10: a separate Crab
        FakeLocalization(3, media.id, 0.5, 0.5, 0.1, 0.1, {"Label": "Crab", "score": 0.7}, frame=10),
    ]
    api = MultiVersionFakeApi(media=media, locs=locs)

    output_path = tmp_path / "export"
    output_path.mkdir()

    ok = download(
        api=api,
        project_id=1,
        group=None,
        depth=None,
        section=None,
        version_list=["v1", "v2"],
        verified=False,
        unverified=False,
        generator=None,
        output_path=output_path,
        labels_list=[],
        concepts_list=[],
        skip_image_download=True,
    )
    assert ok

    lines = (output_path / "labels" / f"{Path(media.name).stem}.txt").read_text().splitlines()
    labels = (output_path / "labels.txt").read_text().split()
    names = sorted(labels[int(line.split()[0])] for line in lines)
    assert names == ["Crab", "Fish"]

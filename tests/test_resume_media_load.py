# mbari_aidata, Apache-2.0 license
# Filename: tests/test_resume_media_load.py
# Description: Tests batched existing-media checks and remainder loading
from types import SimpleNamespace

import pandas as pd

from mbari_aidata.commands.load_common import check_duplicate_media, exclude_loaded_media
from mbari_aidata.plugins.loaders.tator.media import (
    SpecBatcher,
    existing_media_names,
    get_media_ids,
    iter_media_pages,
)


class FakeApi:
    """In-memory stand-in for the media list and count endpoints."""

    def __init__(self, media):
        self.media = list(media)
        self.list_calls = []

    def get_media_count(self, project, type, **kwargs):
        return len(self._filtered(type))

    def get_media_list(self, project, **kwargs):
        self.list_calls.append(kwargs)
        after = kwargs.get("after")
        stop = kwargs.get("stop")
        items = [item for item in self._filtered(kwargs.get("type")) if after is None or item.id > after]
        items = sorted(items, key=lambda item: item.id)
        if stop is not None:
            items = items[:stop]
        return items

    def _filtered(self, media_type):
        return [item for item in self.media if item.type == media_type]


def _media(media_id, name, media_type=1):
    return SimpleNamespace(id=media_id, name=name, type=media_type)


def test_iter_media_pages_follows_id_cursor():
    """Test that media pages advance by the last id instead of a growing offset."""
    api = FakeApi([_media(i, f"f{i}.jpg") for i in range(1, 6)])

    pages = list(iter_media_pages(api, project_id=7, media_type=1, page_size=2))

    assert [[item.id for item in page] for page in pages] == [[1, 2], [3, 4], [5]]
    assert [call.get("after") for call in api.list_calls] == [None, 2, 4]
    assert all("start" not in call for call in api.list_calls)
    assert all(call["sort_by"] == ["$id"] for call in api.list_calls)


def test_iter_media_pages_forwards_extra_filters():
    """Test that section and other filters are included in each media page request."""
    api = FakeApi([_media(1, "a.jpg")])

    pages = list(iter_media_pages(api, project_id=7, media_type=1, page_size=10, section=4))

    assert len(pages) == 1
    assert api.list_calls[0]["section"] == 4
    assert api.list_calls[0]["type"] == 1


def test_iter_media_pages_stops_when_cursor_does_not_advance():
    """Test that a page which repeats the same ids does not loop forever."""

    class StuckApi(FakeApi):
        def get_media_list(self, project, **kwargs):
            self.list_calls.append(kwargs)
            return self.media[:2]

    api = StuckApi([_media(1, "a.jpg"), _media(2, "b.jpg"), _media(3, "c.jpg")])

    pages = list(iter_media_pages(api, project_id=7, media_type=1, page_size=2))

    assert len(pages) == 2
    assert len(api.list_calls) == 2


def test_existing_media_names_stops_when_every_name_is_found():
    """Test that the existing-media scan stops once the requested names are found."""
    api = FakeApi([_media(i, f"f{i}.jpg") for i in range(1, 11)])

    found = existing_media_names(api, 7, 1, ["f1.jpg", "f2.jpg"], page_size=2)

    assert found == {"f1.jpg", "f2.jpg"}
    assert len(api.list_calls) == 1


def test_existing_media_names_reads_later_pages():
    """Test that a file name past the first page is still found."""
    api = FakeApi([_media(i, f"f{i}.jpg") for i in range(1, 6)])

    found = existing_media_names(api, 7, 1, ["f5.jpg"], page_size=2)

    assert found == {"f5.jpg"}
    assert len(api.list_calls) == 3


def test_existing_media_names_matches_case_insensitively():
    """Test that a stored name matches a candidate that differs only by case."""
    api = FakeApi([_media(1, "Frame.JPG")])

    found = existing_media_names(api, 7, 1, ["frame.jpg"], page_size=10)

    assert found == {"frame.jpg"}


def test_existing_media_names_is_empty_when_project_has_no_media():
    """Test that an empty project does not page media."""
    api = FakeApi([])

    found = existing_media_names(api, 7, 1, ["a.jpg"])

    assert found == set()
    assert api.list_calls == []


def test_check_duplicate_media_uses_one_page_for_many_files():
    """Test that duplicate detection does not request each file name separately."""
    api = FakeApi([_media(1, "keep.jpg"), _media(2, "skip.jpg")])
    df_media = pd.DataFrame({"media_path": ["/data/keep.jpg", "/data/new.jpg", "/data/skip.jpg"]})

    duplicates = check_duplicate_media(api, 7, 1, df_media)

    assert duplicates == ["keep.jpg", "skip.jpg"]
    assert len(api.list_calls) == 1


def test_exclude_loaded_media_returns_the_remainder():
    """Test that files already in the project are removed and the rest are kept."""
    api = FakeApi([_media(1, "keep.jpg")])
    df_media = pd.DataFrame(
        {
            "media_path": ["/data/keep.jpg", "/data/new.jpg"],
            "media_type": ["image", "image"],
        }
    )

    kept = exclude_loaded_media(api, 7, 1, df_media)

    assert list(kept["media_path"]) == ["/data/new.jpg"]


def test_get_media_ids_indexes_every_returned_media():
    """Test that name-to-id lookup reads paged media without an offset."""
    api = FakeApi([_media(i, f"f{i}.jpg") for i in (1, 2, 3)])
    project = SimpleNamespace(id=7, name="proj")

    media_map = get_media_ids(api, project, 1)

    assert media_map == {"f1.jpg": 1, "f2.jpg": 2, "f3.jpg": 3}
    assert len(api.list_calls) == 1
    assert "start" not in api.list_calls[0]


def test_spec_batcher_flushes_full_batches_and_a_remainder():
    """Test that specs are created in batches instead of one request for the whole load."""
    created_batches = []

    def create(specs):
        created_batches.append([spec["name"] for spec in specs])
        return list(range(len(specs)))

    batcher = SpecBatcher(create, batch_size=2)
    for name in ["a", "b", "c", "d", "e"]:
        assert batcher.add({"name": name})
    assert batcher.flush()

    assert created_batches == [["a", "b"], ["c", "d"], ["e"]]
    assert batcher.ids == [0, 1, 0, 1, 0]


def test_spec_batcher_stops_after_a_failed_batch():
    """Test that a failed create stops further batches and reports failure."""

    def create(specs):
        if specs[0]["name"] == "c":
            return None
        return [1] * len(specs)

    batcher = SpecBatcher(create, batch_size=2)
    assert batcher.add({"name": "a"})
    assert batcher.add({"name": "b"})
    assert batcher.add({"name": "c"})
    assert not batcher.add({"name": "d"})

    assert batcher.failed
    assert batcher.ids == [1, 1]
    assert not batcher.flush()

# mbari_aidata, Apache-2.0 license
# Filename: tests/test_attribute_dict.py
# Description: Unit tests for fetch_attribute_dict – no live Tator instance required
from unittest.mock import MagicMock

import pytest

from mbari_aidata.plugins.loaders.tator.attribute_utils import fetch_attribute_dict
from mbari_aidata.commands.load_common import get_media_attributes


# ---------------------------------------------------------------------------
# Helpers – build lightweight mock attribute-type objects
# ---------------------------------------------------------------------------

def _make_attr(name: str, dtype: str) -> MagicMock:
    a = MagicMock()
    a.name = name
    a.dtype = dtype
    return a


def _make_media_type(name: str, dtype: str, attrs) -> MagicMock:
    mt = MagicMock()
    mt.name = name
    mt.dtype = dtype
    mt.attribute_types = attrs
    return mt


def _make_loc_type(name: str, dtype: str, attrs) -> MagicMock:
    lt = MagicMock()
    lt.name = name
    lt.dtype = dtype
    lt.attribute_types = attrs
    return lt


def _make_state_type(name: str, attrs) -> MagicMock:
    st = MagicMock()
    st.name = name
    st.attribute_types = attrs
    return st


def _build_api():
    """Return a mock TatorApi with a realistic project schema."""
    api = MagicMock()

    api.get_media_type_list.return_value = [
        _make_media_type("Image", "image", [
            _make_attr("video_reference_uuid", "string"),
            _make_attr("iso_start_datetime", "datetime"),
        ]),
        _make_media_type("Video", "video", [
            _make_attr("video_reference_uuid", "string"),
            _make_attr("depth", "float"),
        ]),
    ]

    api.get_localization_type_list.return_value = [
        _make_loc_type("Box", "box", [
            _make_attr("Label", "string"),
            _make_attr("score", "float"),
            _make_attr("cluster", "string"),
            _make_attr("verified", "bool"),
        ]),
        _make_loc_type("TDWA Box", "box", [
            _make_attr("Label", "string"),
            _make_attr("avg_score", "float"),
        ]),
    ]

    api.get_state_type_list.return_value = [
        _make_state_type("Track State", [
            _make_attr("label", "string"),
            _make_attr("avg_score", "float"),
            _make_attr("max_score", "float"),
        ]),
    ]

    return api


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestFetchAttributeDict:
    def setup_method(self):
        self.api = _build_api()
        self.result = fetch_attribute_dict(self.api, project_id=42)

    def test_api_called_with_correct_project(self):
        self.api.get_media_type_list.assert_called_once_with(project=42)
        self.api.get_localization_type_list.assert_called_once_with(project=42)
        self.api.get_state_type_list.assert_called_once_with(project=42)

    # Media types
    def test_image_dtype_key_present(self):
        assert "image" in self.result

    def test_image_attributes_correct(self):
        attrs = self.result["image"]["attributes"]
        assert attrs["video_reference_uuid"] == {"type": "string"}
        assert attrs["iso_start_datetime"] == {"type": "datetime"}

    def test_video_dtype_key_present(self):
        assert "video" in self.result

    def test_video_attributes_correct(self):
        attrs = self.result["video"]["attributes"]
        assert attrs["video_reference_uuid"] == {"type": "string"}
        assert attrs["depth"] == {"type": "float"}

    def test_image_name_key_also_registered(self):
        # "Image" → "image" name key (same as dtype here, still present)
        assert "image" in self.result

    # Localization types
    def test_primary_box_dtype_key_present(self):
        assert "box" in self.result

    def test_primary_box_attributes_correct(self):
        # "box" dtype key should map to the *first* localization type ("Box")
        attrs = self.result["box"]["attributes"]
        assert "Label" in attrs
        assert "score" in attrs
        assert "verified" in attrs

    def test_tdwa_box_name_key_present(self):
        assert "tdwa_box" in self.result

    def test_tdwa_box_attributes_correct(self):
        attrs = self.result["tdwa_box"]["attributes"]
        assert attrs["Label"] == {"type": "string"}
        assert attrs["avg_score"] == {"type": "float"}

    # State types
    def test_track_state_key_present(self):
        assert "track_state" in self.result

    def test_track_state_attributes_correct(self):
        attrs = self.result["track_state"]["attributes"]
        assert attrs["label"] == {"type": "string"}
        assert attrs["avg_score"] == {"type": "float"}
        assert attrs["max_score"] == {"type": "float"}

    def test_no_extra_keys_from_state(self):
        # State types should NOT produce a dtype key (they have no dtype)
        assert "media" not in self.result
        assert "localization" not in self.result

    def test_returns_dict(self):
        assert isinstance(self.result, dict)


class TestFetchAttributeDictEmptyProject:
    """Edge case: project with no types defined."""

    def test_empty_project_returns_empty_dict(self):
        api = MagicMock()
        api.get_media_type_list.return_value = []
        api.get_localization_type_list.return_value = []
        api.get_state_type_list.return_value = []
        result = fetch_attribute_dict(api, project_id=1)
        assert result == {}


class TestFetchAttributeDictNoneAttributeTypes:
    """Edge case: attribute_types is None (some Tator versions return None)."""

    def test_none_attribute_types_handled(self):
        api = MagicMock()
        mt = _make_media_type("Image", "image", None)
        api.get_media_type_list.return_value = [mt]
        api.get_localization_type_list.return_value = []
        api.get_state_type_list.return_value = []
        result = fetch_attribute_dict(api, project_id=1)
        assert result["image"]["attributes"] == {}


class TestGetMediaAttributesWithApi:
    """Tests for the updated get_media_attributes() helper."""

    def test_returns_from_api_when_provided(self):
        api = _build_api()
        config_dict = {}  # no tator section needed
        attrs = get_media_attributes(config_dict, "image", api=api, project_id=42)
        assert "video_reference_uuid" in attrs

    def test_falls_back_to_config_when_no_api(self):
        config_dict = {
            "tator": {
                "image": {
                    "attributes": {"my_attr": {"type": "string"}}
                }
            }
        }
        attrs = get_media_attributes(config_dict, "image")
        assert attrs == {"my_attr": {"type": "string"}}

    def test_falls_back_to_config_when_type_missing_from_api(self):
        """If the API schema doesn't have the requested type, use config."""
        api = MagicMock()
        api.get_media_type_list.return_value = []
        api.get_localization_type_list.return_value = []
        api.get_state_type_list.return_value = []
        config_dict = {
            "tator": {
                "image": {
                    "attributes": {"fallback_attr": {"type": "int"}}
                }
            }
        }
        attrs = get_media_attributes(config_dict, "image", api=api, project_id=1)
        assert attrs == {"fallback_attr": {"type": "int"}}

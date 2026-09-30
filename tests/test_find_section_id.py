# mbari_aidata, Apache-2.0 license
# Filename: tests/test_find_section_id.py
# Description: Tests resolving a Tator section name to its ID
from types import SimpleNamespace

import pytest

from mbari_aidata.plugins.loaders.tator.common import find_section_id


class _Api:
    def __init__(self, sections):
        self._sections = sections

    def get_section_list(self, project):
        assert project == 12
        return self._sections


def test_find_section_id_returns_matching_section():
    """Test that a section name resolves to that section's ID."""
    api = _Api([SimpleNamespace(id=4, name="2026/04"), SimpleNamespace(id=9, name="2026/05")])
    assert find_section_id(api, 12, "2026/04") == 4


def test_find_section_id_rejects_unknown_section():
    """Test that a missing section name is rejected."""
    api = _Api([SimpleNamespace(id=4, name="2026/04")])
    with pytest.raises(ValueError, match="Could not find section 2026/03"):
        find_section_id(api, 12, "2026/03")

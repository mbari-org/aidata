# mbari_aidata, Apache-2.0 license
# Filename: tests/test_roi_crop_filter.py
# Description: Tests the build_roi_crop_filter function
from mbari_aidata.generators.utils import build_roi_crop_filter


def test_build_roi_crop_filter_clips_without_fill():
    # Tall box near the left edge: squaring expands horizontally past x=0.
    result = build_roi_crop_filter(10, 50, 60, 150, 200, 200)
    assert result == "crop=85:100:0:50"


def test_build_roi_crop_filter_pads_with_white():
    result = build_roi_crop_filter(10, 50, 60, 150, 200, 200, fill="white")
    assert result == "crop=85:100:0:50,pad=100:100:15:0:white"


def test_build_roi_crop_filter_pads_with_black_and_resize():
    result = build_roi_crop_filter(170, 50, 210, 150, 200, 200, resize=224, fill="black")
    assert result == "crop=60:100:140:50,pad=100:100:0:0:black,scale=224:224"


def test_build_roi_crop_filter_pads_bottom_edge():
    result = build_roi_crop_filter(50, 170, 150, 210, 200, 200, fill="white")
    assert result == "crop=100:60:50:140,pad=100:100:0:0:white"

# mbari_aidata, Apache-2.0 license
# Filename: commands/dataset_paths.py
# Description: Shared helpers for resolving dataset directory layouts, e.g. the "images"/"media" rename

from pathlib import Path
from typing import Optional

# Directory names checked, in priority order, when looking for a dataset's image/media directory.
# "images" is the name used by datasets produced by older versions of `aidata download`; "media" is
# the current directory name. Both are accepted so downstream commands work with either layout.
IMAGE_DIR_NAMES = ("images", "media")


def resolve_image_dir(base_path: Path) -> Optional[Path]:
    """
    Resolve the image/media directory under base_path, accepting either "images" or "media" as
    the directory name.

    :param base_path: Dataset root directory
    :return: The resolved directory Path, or None if neither "images" nor "media" exists
    """
    for name in IMAGE_DIR_NAMES:
        candidate = Path(base_path) / name
        if candidate.exists():
            return candidate
    return None

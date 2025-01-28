# mbari_aidata, Apache-2.0 license
# Filename: plugins/extractor/media_types.py
# Description: Enumerator class for different media types
from enum import Enum

class MediaType(Enum):
    VIDEO = "VIDEO"
    IMAGE = "IMAGE"
    AUDIO = "AUDIO"
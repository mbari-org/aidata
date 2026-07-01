# mbari_aidata, Apache-2.0 license
# Filename: plugins/loaders/tator/attribute_utils.py
# Description: Attribute type utilities and API-driven attribute dictionary builder
from datetime import datetime
from typing import Dict

import pandas as pd
import pytz


def attribute_to_dict(attribute):
    """Converts a Tator attribute to a dictionary."""
    return {attr.key: attr.value for attr in attribute}


def fetch_attribute_dict(api, project_id: int) -> Dict[str, dict]:
    """
    Queries Tator for all media, localization, and state attribute definitions
    in a project and returns a dict compatible with the ``tator:`` section of
    ``config.yml``.

    This lets callers build the attribute mapping at runtime from the live
    project schema instead of hard-coding it in a YAML file.

    Keys follow these conventions:

    * **Media types** — keyed by ``dtype`` (``"image"`` or ``"video"``).
      When multiple media types share the same dtype their attributes are
      merged; the first type encountered also registers a name-based key
      (``type_name.lower().replace(" ", "_")``).
    * **Localization types** — keyed by ``dtype`` (``"box"``, ``"line"``,
      ``"dot"``).  A name-based key is also registered so that distinct
      types with the same dtype (e.g. ``"Box"`` and ``"TDWA Box"``) remain
      individually addressable.
    * **State types** — keyed by name (lowercased, spaces replaced with
      underscores), e.g. ``"track_state"``.

    Each entry has the shape::

        {
            "<key>": {
                "attributes": {
                    "<attr_name>": {"type": "<dtype>"},
                    ...
                }
            }
        }

    :param api: :class:`tator.openapi.tator_openapi.TatorApi` instance.
    :param project_id: Tator project ID.
    :return: Attribute dictionary keyed by type name/dtype.
    """
    result: Dict[str, dict] = {}

    # --- Media types (image / video) ---
    for mt in api.get_media_type_list(project=project_id):
        attrs = {a.name: {"type": a.dtype} for a in (mt.attribute_types or [])}
        dtype_key = mt.dtype  # "image" or "video"
        name_key = mt.name.lower().replace(" ", "_")

        # Merge into the dtype-keyed bucket (backward-compat with config.yml)
        if dtype_key not in result:
            result[dtype_key] = {"attributes": attrs}
        else:
            result[dtype_key]["attributes"].update(attrs)

        # Also register under the type name so named lookups work
        if name_key not in result:
            result[name_key] = {"attributes": attrs}

    # --- Localization types (box / line / dot) ---
    for lt in api.get_localization_type_list(project=project_id):
        attrs = {a.name: {"type": a.dtype} for a in (lt.attribute_types or [])}
        dtype_key = lt.dtype  # "box", "line", or "dot"
        name_key = lt.name.lower().replace(" ", "_")

        # Name-based key for uniquely addressable types (e.g. "tdwa_box")
        result[name_key] = {"attributes": attrs}

        # dtype key: first type wins so "box" maps to the primary Box type
        if dtype_key not in result:
            result[dtype_key] = {"attributes": attrs}

    # --- State types ---
    for st in api.get_state_type_list(project=project_id):
        attrs = {a.name: {"type": a.dtype} for a in (st.attribute_types or [])}
        key = st.name.lower().replace(" ", "_")
        result[key] = {"attributes": attrs}

    return result


def format_attributes(attributes: dict, attribute_mapping: dict) -> dict:
    """Formats attributes according to the attribute mapping."""
    attributes_ = {}
    for a_key, a_value in attributes.items():
        for m_key, m_value in attribute_mapping.items():
            a_key = a_key.lower()
            m_key = m_key.lower()
            m_key = m_key.lower()
            if a_key == m_key:
                if m_value["type"] == "datetime":
                    # Truncate datetime to milliseconds, convert to UTC, and format as ISO 8601
                    if isinstance(attributes[a_key], datetime) and attributes[a_key] is not pd.NaT:
                        dt_utc = attributes[a_key].astimezone(pytz.utc)
                        try:
                            dt_str = dt_utc.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                            dt_str = dt_str[:-3] + "Z"
                        except ValueError:
                            dt_str = dt_utc.strftime("%Y-%m-%dT%H:%M:%SZ")
                    else:
                        dt_str = attributes[a_key]
                    attributes_[a_key] = dt_str
                # Convert boolean to string
                elif m_value["type"] == "bool":
                    if attributes[m_key] == 1:
                        attributes_[m_key] = "True"
                    else:
                        attributes_[m_key] = "False"
                # Convert enum to string
                elif m_value["type"] == "enum":
                    if attributes[m_key] is None:
                        attributes_[m_key] = "UNKNOWN"
                    else:
                        attributes_[m_key] = str(attributes[m_key])
                elif m_value["type"] == "float":
                    if attributes[m_key] is None:
                        attributes_[m_key] = -1
                    else:
                        attributes_[m_key] = float(attributes[m_key])
                elif m_value["type"] == "int":
                    if attributes[m_key] is None:
                        attributes_[m_key] = -1
                    else:
                        attributes_[m_key] = int(attributes[m_key])
                elif m_value["type"] == "string":
                    if m_key == "cluster":
                        attributes_[m_key] = f"Unknown C{attributes[m_key]}"
                    else:
                        attributes_[m_key] = str(attributes[m_key])
                else:
                    raise TypeError(f"Unknown type {m_value['type']} - do not know how to format {m_key}")
    return attributes_


def _find_types(api, project):
    """Returns dict containing mapping from dtype to type."""
    loc_types = api.get_localization_type_list(project)
    state_types = api.get_state_type_list(project)
    loc_types = {loc_type.dtype: loc_type for loc_type in loc_types}
    state_types = {state_type.association: state_type for state_type in state_types}
    return loc_types, state_types

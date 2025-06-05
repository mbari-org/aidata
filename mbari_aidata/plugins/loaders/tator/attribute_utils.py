# mbari_aidata, Apache-2.0 license
# Filename: plugins/loaders/tator/attribute_utils.py
# Description:  Database types
from datetime import datetime

import pytz


def attribute_to_dict(attribute):
    """Converts a Tator attribute to a dictionary."""
    return {attr.key: attr.value for attr in attribute}


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
                    if isinstance(attributes[a_key], datetime):
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

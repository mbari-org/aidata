# aidata, Apache-2.0 license
# Filename: database/data_types.py
# Description:  Database types

import pytz


def attribute_to_dict(attribute):
    """Converts a Tator attribute to a dictionary."""
    return {attr.key: attr.value for attr in attribute}


def format_attributes(attributes: dict, attribute_mapping: dict) -> dict:
    """Formats attributes according to the attribute mapping."""
    for a_key, a_value in attributes.items():
        for m_key, m_value in attribute_mapping.items():
            if a_key == m_key:
                # Truncate datetime to milliseconds, convert to UTC, and format as ISO 8601
                if m_value["type"] == "datetime":
                    dt_utc = attributes["iso_datetime"].astimezone(pytz.utc)
                    dt_str = dt_utc.strftime("%Y-%m-%dT%H:%M:%S.%fZ")
                    dt_str = dt_str[:-3] + "Z"
                    attributes[a_key] = dt_str
                # Convert boolean to string
                if m_value["type"] == "bool":
                    if attributes[m_key] == 1:
                        attributes[m_key] = "True"
                    else:
                        attributes[m_key] = "False"
                if m_value["type"] == "float":
                    attributes[m_key] = float(attributes[m_key])
                if m_value["type"] == "int":
                    attributes[m_key] = int(attributes[m_key])
    return attributes


def _find_types(api, project):
    """Returns dict containing mapping from dtype to type."""
    loc_types = api.get_localization_type_list(project)
    state_types = api.get_state_type_list(project)
    loc_types = {loc_type.dtype: loc_type for loc_type in loc_types}
    state_types = {state_type.association: state_type for state_type in state_types}
    return loc_types, state_types


if __name__ == "__main__":
    _find_types()

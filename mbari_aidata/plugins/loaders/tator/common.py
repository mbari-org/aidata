# mbari_aidata, Apache-2.0 license
# Filename: plugins/loaders/tator/common.py
# Description: Common database functions
import os
from datetime import date, datetime
from typing import Tuple, Any, List, Dict

import yaml

from tator.openapi.tator_openapi import TatorApi  # type: ignore
from tator.openapi.tator_openapi.models import Project  # type: ignore
import tator  # type: ignore
from urllib3 import HTTPHeaderDict

from mbari_aidata.logger import info, debug, err


def get_version_id(api: TatorApi, project: Project, version: str) -> int:
    """
    Get the version ID for the given project
    :param api: :class:`TatorApi` object
    :param project: project object
    :param version: version name
    :return: version ID
    """
    versions = api.get_version_list(project=project.id)
    debug(versions)

    # Find the version by name
    version_match = [v for v in versions if v.name == version]
    if len(version_match) == 0:
        err(f"Could not find version {version}")
        raise ValueError(f"Could not find version {version}")
    if len(version_match) > 1:
        err(f"Found multiple versions with name {version}")
        raise ValueError(f"Found multiple versions with name {version}")
    return version_match[0].id


def init_api_project(host: str, token: str, project: str) -> Tuple[TatorApi, tator.models.Project]:
    """
    Fetch the Tator API and project
    :param host: hostname, e.g. localhost
    :param token: api token
    :param project:  project name
    :return:
    """
    try:
        info(f"Connecting to Tator at {host}")
        api = tator.get_api(host, token)
    except Exception as e:
        raise e

    info(f"Searching for project {project} on {host}.")
    tator_project = find_project(api, project)
    if tator_project is None:
        raise Exception(f"Could not find project {project}")
    info(f"Found project {tator_project.name} with id {tator_project.id}")
    if tator_project is None:
        raise Exception(f"Could not find project {project}")

    return api, tator_project


def find_project(api: TatorApi, project_name: str) -> tator.models.Project:
    """
    Find the project with the given name
    :param api: :class:`TatorApi` object
    :param project_name: Name of the project
    """
    projects = api.get_project_list()
    info(f"Found {len(projects)} projects")
    for p in projects:
        if p.name == project_name:
            return p
    return None


def find_box_type(api: TatorApi, project: int, type_name: str = "Box") -> tator.models.LocalizationType:
    """
    Find the box type for the given project
    :param type_name:  String that identifies type, e.g. "Box"
    :param api: :class:`TatorApi` object
    :param project: project ID
    """
    types = api.get_localization_type_list(project=project)
    for t in types:
        if t.name == type_name:
            return t
    return None


def find_media_type(api: TatorApi, project: int, type_name: str) -> Any | None:
    """
    Find the media type for the given project
    :param type_name: String that identifies type, e.g. "Stereo"
    :param api: :class:`TatorApi` object
    :param project: project ID
    """
    types = api.get_media_type_list(project=project)
    for t in types:
        if t.name == type_name:
            return t
    return None


def init_yaml_config(yaml_config: str) -> dict:
    """
    # Get the configuration from the YAML file
    :param yaml_config: The YAML configuration file
    :return: The configuration dictionary
    """
    info(f"Reading configuration from {yaml_config}")
    if not os.path.exists(yaml_config):
        info(f"Configuration file {yaml_config} not found")
        raise FileNotFoundError(f"Configuration file {yaml_config} not found")
    with open(yaml_config, "r") as file:
        try:
            config_dict = yaml.safe_load(file)
        except yaml.YAMLError as e:
            err(f"Error reading YAML file: {e}")
            raise e
    return config_dict

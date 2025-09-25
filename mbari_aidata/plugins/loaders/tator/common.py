# mbari_aidata, Apache-2.0 license
# Filename: plugins/loaders/tator/common.py
# Description: Common database functions
import os
from typing import Tuple, Any
from urllib.parse import urlparse

import yaml
from tator.openapi import tator_openapi

from tator.openapi.tator_openapi import TatorApi, CreateListResponse, CreateResponse  # type: ignore
from tator.openapi.tator_openapi.models import Project  # type: ignore
import tator  # type: ignore

from mbari_aidata.logger import info, debug, err


def create_version(api: TatorApi, project: Project, version: str) -> int:
    """
    Create a version in the given project
    :param api: :class:`TatorApi` object
    :param project: project object
    :param version: version name
    :return: version ID
    """
    try:
        # Create another version that is based off the baseline
        baseline_version = api.get_version_list(project.id)[0].id
        version_obj = api.create_version(project.id, version_spec={
            "name": version,
            "description": version,
            "show_empty": True,
            "bases": [baseline_version]
            })
        return version_obj.id
    except Exception as e:
        err(f"Error creating version {version}: {e}")
        raise e

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

    # Flag and error if the version is empty
    if version is None or len(version) == 0:
        raise Exception(f"A version must be specified, e.g. Baseline")

    # Find the version by name
    version_match = [v for v in versions if v.name == version]
    if len(version_match) == 0:
        err(f"Could not find version {version}")
        version_id = create_version(api, project, version)
        return version_id
    if len(version_match) > 1:
        err(f"Found multiple versions with name {version}")
        raise ValueError(f"Found multiple versions with name {version}")
    return version_match[0].id

def get_api(host='https://cloud.tator.io', token=os.getenv('TATOR_TOKEN'), disable_ssl_verify=False) -> TatorApi:
    """ Retrieves a :class:`tator.api` instance using the given host and token.

    :param host: URL of host. Default is https://cloud.tator.io.
    :param token: API token.
    :param disable_ssl_verify: Disable SSL verification
    :returns: :class:`tator.api` object.
    """
    config = tator_openapi.Configuration()
    config.host = host
    if disable_ssl_verify:
        config.verify_ssl = False
    if token:
        config.api_key['Authorization'] = token
        config.api_key_prefix['Authorization'] = 'Token'

    api = tator_openapi.TatorApi(tator_openapi.ApiClient(config))
    api._create_media_list_impl = api.create_media_list

    def create_media_list_wrapper(*args, **kwargs):
        response = api._create_media_list_impl(*args, **kwargs)
        if "id" in response and isinstance(response["id"], list):
            try:
                return CreateListResponse(**response)
            except Exception:
                return response
        try:
            return CreateResponse(**response)
        except Exception:
            return response

    api.create_media_list = create_media_list_wrapper
    def legacy_create_media(project, media_spec, **kwargs):
        return api.create_media_list(project, media_spec, **kwargs)

    api.create_media = legacy_create_media
    return api

def init_api_project(host: str, token: str, project: str, disable_ssl_verify=False) -> Tuple[TatorApi, tator.models.Project]:
    """
    Fetch the Tator API and project
    :param host: hostname, e.g. localhost
    :param token: api token
    :param project:  project name
    :param disable_ssl_verify: Disable SSL verification
    :return:
    """
    try:
        info(f"Connecting to Tator at {host}")
        api = get_api(host=host, token=token, disable_ssl_verify=disable_ssl_verify)
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
    parsed_url = urlparse(str(yaml_config))

    if parsed_url.scheme in ('http', 'https'):
        import requests
        response = requests.get(yaml_config)
        response.raise_for_status()
        content = response.content.decode()
    else:
        if not os.path.exists(yaml_config):
            info(f"Configuration file {yaml_config} not found")
            raise FileNotFoundError(f"Configuration file {yaml_config} not found")
        with open(yaml_config) as f:
            content = f.read()

    try:
        config_dict = yaml.safe_load(content)
    except yaml.YAMLError as e:
        err(f"Error reading YAML file: {e}")
        raise e
    return config_dict

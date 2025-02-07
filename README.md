[![MBARI](https://www.mbari.org/wp-content/uploads/2014/11/logo-mbari-3b.png)](http://www.mbari.org)
[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/semantic-release/semantic-release)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/downloads/)

*mbari-aidata* is a command line tool to do extract, transform, load and download operations
on AI data for a number of projects at MBARI that require detection, clustering or classification
workflows.

More documentation and examples are available at [https://docs.mbari.org/internal/ai/data](https://docs.mbari.org/internal/ai/data/).
 
Features:

* Loading object detection/classification/clustering output from [SDCAT](https://github.com/mbari-org/sdcat) formatted output
* Downloads from [Tator](https://www.tatorapp.com/) into various formats for machine learning, e.g. COCO, CIFAR, or PASCAL VOC format.
* Uploads triggered from a [Redis](https://redis.io) queue for workflows that need real-time loads. 
* Loading metadata from SONY cameras, extracting timestamps from images and video, and loading VOC formatted data.  The plugin
architecture allows for easy extension to other data sources and formats.  Media loads are generally handled in a
project specific way by the [plugin/extractors](https://github.com/mbari-org/aidata/tree/main/mbari_aidata/plugins/extractors)
module.
* Media must exist through a URL accessible by the Tator server.  The media may be checked for duplicates and uploaded if necessary.
* Augmentations are available for VOC downloaded data to create more training data using the [albumentations library](https://albumentations.ai/)

## Requirements
- Python 3.10 or higher
- A Tator API token and Redis password for the .env file. Contact the MBARI AI team for access.
- Docker for development and testing only, but it can also be used instead of a local Python installation.

## Installation 
Install as a Python package:

```shell
pip install mbari-aidata
```
 
Create the .env file with the following contents in the root directory of the project:
```shell
TATOR_TOKEN=your_api_token
REDIS_PASSWORD=your_redis_password
ENVIRONMENT=testing or production
```

Create a configuration file in the root directory of the project:
```shell
touch config_cfe.yaml
```

This file will be used to configure the project data, such as mounts, plugins, and database connections.
```shell
aidata download --version Baseline --labels "Diatoms, Copepods" --config config_cfe.yml
```

Example configuration file:
```yaml
# config_cfe.yml
# Config file for CFE project production
mounts:
  - name: "image"
    path: "/mnt/CFElab"
    host: "mantis.shore.mbari.org"
    nginx_root: "/CFElab"

  - name: "video"
    path: "/mnt/CFElab"
    host: "mantis.shore.mbari.org"
    nginx_root: "/CFElab"


plugins:
  - name: "extractor"
    module: "mbari_aidata.plugins.extractors.tap_cfe_media"
    function: "extract_media"

redis:
  host: "doris.shore.mbari.org"
  port: 6382

vss:
  project: "902111-CFE"
  model: "google/vit-base-patch16-224"

tator:
  project: "902111-CFE"
  host: "mantis.shore.mbari.org"
  image:
    attributes:
      iso_datetime:
        type: datetime
      depth:
        type: float
  video:
    attributes:
      iso_start_datetime:
        type: datetime
  box:
    attributes:
      Label:
        type: string
      score:
        type: float
      cluster:
        type: string
      saliency:
        type: float
      area:
        type: int
      exemplar:
        type: bool
```

A docker version is also available at `mbari/aidata:latest` or `mbari/aidata:latest:cuda-124`.
For example, to download data using the docker image:

```shell
docker run -it --rm -v $(pwd):/mnt mbari/aidata:latest aidata download --version Baseline --labels "Diatoms, Copepods" --config config_cfe.yml
```

## Commands

* `aidata download --help` -  Download data, such as images, boxes, into various formats for machine learning e,g, COCO, CIFAR, or PASCAL VOC format
* `aidata load --help` -  Load data, such as images, and boxes into either a Postgres or REDIS database
* `aidata db --help` -  Commands related to database management
* `aidata transform --help` - Commands related to transforming downloaded data
* `aidata  -h` - Print help message and exit.
 
Source code is available at [github.com/mbari-org/aidata](https://github.com/mbari-org/aidata/). 

## Development
See the [Development Guide](https://github.com/mbari-org/aidata/blob/main/DEVELOPMENT.md) for more information on how to set up the development environment.

**updated: 2025-02-04**
[![MBARI](https://www.mbari.org/wp-content/uploads/2014/11/logo-mbari-3b.png)](http://www.mbari.org)
[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/semantic-release/semantic-release)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/downloads/)

*aidata* is a command line tool to do extract, transform, load and download operations
on AI data for a number of projects at MBARI that require detection, clustering or classification
workflows.

Full documentation is available on commands at [https://docs.mbari.org/internal/ai/data](https://docs.mbari.org/internal/ai/data/).
 
This supports loading [sdcat](https://github.com/mbari-org/sdcat) formatted output and downloads from [Tator](https://www.tatorapp.com/) and 
[Redis](https://redis.io) databases, although support for other data sources is also possible, e.g. [FathomNet](https://fathomnet.org/).
so we decided to keep the name generic.

This also supports loading media from a directory or URL, and transforming data into various 
formats for machine learning, e.g. COCO, CIFAR, or PASCAL VOC format.

## Requirements
- Python 3.10 or higher
- A Tator API token and Redis password for the .env file. Contact the MBARI AI team for access.
- Docker for development and testing only

## Installation 
Install from PyPi

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
mbari_aidata download --version Baseline --labels "Diatoms, Copepods" --config config_cfe.yml
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

## Commands

* `mbari_aidata download --help` -  Download data, such as images, boxes, into various formats for machine learning e,g, COCO, CIFAR, or PASCAL VOC format
* `mbari_aidata load --help` -  Load data, such as images, and boxes into either a Postgres or REDIS database
* `mbari_aidata db --help` -  Commands related to database management
* `mbari_aidata transform --help` - Commands related to transforming downloaded data
* `mbari_aidata  -h` - Print help message and exit.
 
Source code is available at [github.com/mbari-org/aidata](https://github.com/mbari-org/aidata/). 

## Development
See the [Development Guide](DEVELOPMENT.md) for more information on how to set up the development environment.

**updated: 2025-01-28**
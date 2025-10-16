[![MBARI](https://www.mbari.org/wp-content/uploads/2014/11/logo-mbari-3b.png)](http://www.mbari.org)
[![semantic-release](https://img.shields.io/badge/%20%20%F0%9F%93%A6%F0%9F%9A%80-semantic--release-e10079.svg)](https://github.com/semantic-release/semantic-release)
[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/downloads/)

*mbari-aidata* is a command line tool to do extract, transform, load (ETL) and download operations
on AI data for a number of projects at MBARI that require detection, clustering or classification
workflows.  This tool is designed to work with [Tator](https://www.tator.io/), a web based
platform for video and image annotation and data management and [Redis](https://redis.io/) 
queues for ingesting data from real-time workflows.

===========

More documentation and examples are available at [https://docs.mbari.org/internal/ai/data](https://docs.mbari.org/internal/ai/data/).
 
## 🚀 Features
* 🧠 Object Detection/Clustering Integration: Loads detection/classification/clustering output from SDCAT formatted results.
* Flexible Data Export: Downloads from Tator into machine learning formats like COCO, CIFAR, or PASCAL VOC.
* Crop localizaions into optimized datasets for training classification models.
* Real-Time Uploads: Pushes localizations to [Tator](https://www.tator.io/) via [Redis](https://redis.io/glossary/redis-queue/) queues for real-time workflows.
* Metadata Extraction: Parses images metadata such as GPS/time/date through a plugin-based system (extractors).
* Duplicate Detection & flexible media references: Supports duplicate media load checks with the --check-duplicates flag. 
* Images or video are loaded through a web server without needing to upload or move them from your internal NFS project mounts (e.g. Thalassa)
* Combine multiple data versions into a single dataset for training or evaluation using the --version flag with comma separated values. Data is combined through Non-Maximum Suppression (NMS) to remove duplicate boxes.
* Augmentation Support: Augment VOC datasets with [Albumentations](https://albumentations.ai/) to boost your object detection model performance.

## Requirements
- Python 3.10 or higher
- A Tator API token and (optional) Redis password for the .env file. Contact the MBARI AI team for access.
- 🐳Docker for development and testing only, but it can also be used instead of a local Python installation.
- For local installation, you will need to install the required Python packages listed in the `requirements.txt` file, [ffmpeg](https://ffmpeg.org/), and the mp4dump tool from https://www.bento4.com/

## 📦 Installation 
Install as a Python package:

```shell
pip install mbari-aidata
```
 
Create the .env file with the following contents in the root directory of the project:

```text
TATOR_TOKEN=your_api_token
REDIS_PASSWORD=your_redis_password
ENVIRONMENT=testing or production
```

Create a configuration file in the root directory of the project:
```bash
touch config_cfe.yaml
```
Or, use the project specific configuration from our docs server at
https://docs.mbari.org/internal/ai/projects/


This file will be used to configure the project data, such as mounts, plugins, and database connections.
```bash
aidata download --version Baseline --labels "Diatoms, Copepods" --config https://docs.mbari.org/internal/ai/projects/uav-901902/config_uav.yml
```

⚙️Example configuration file:
```yaml
# config_cfe.yml
# Config file for CFE project production
mounts:
  - name: "image"
    path: "/mnt/CFElab"
    host: "https://mantis.shore.mbari.org"
    nginx_root: "/CFElab"

  - name: "video"
    path: "/mnt/CFElab"
    host: "https://mantis.shore.mbari.org"
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
  host: "https://mantis.shore.mbari.org"
  image:
    attributes:
      iso_datetime: #<-------Required for images
        type: datetime
      depth:
        type: float
  video:
    attributes:
      iso_start_datetime:  #<-------Required for videos
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

## 🐳 Docker usage
A docker version is also available at `mbari/aidata:latest` or `mbari/aidata:latest:cuda-124`.
For example, to download data from version Baseline using the docker image:

```shell
docker run -it --rm -v $(pwd):/mnt mbari/aidata:latest aidata download --version Baseline --labels "Diatoms, Copepods" --config config_cfe.yml
```

to download multiple versions
```shell
docker run -it --rm -v $(pwd):/mnt mbari/aidata:latest aidata download --version Baseline,ver0 --labels "Diatoms, Copepods" --config config_cfe.yml`
```
 
## Commands

* `aidata download --help` -  Download data, such as images, boxes, into various formats for machine learning e.g. COCO, CIFAR, or PASCAL VOC format. Augmentation supported for VOC exported data using Albumentations.
* `aidata load --help` -  Load data, such as images, boxes, or clusters into either a Postgres or REDIS database
* `aidata db --help` -  Commands related to database management
* `aidata transform --help` - Commands related to transforming downloaded data
* `aidata  -h` - Print help message and exit.
 
Source code is available at [github.com/mbari-org/aidata](https://github.com/mbari-org/aidata/). 

## Development
See the [Development Guide](https://github.com/mbari-org/aidata/blob/main/DEVELOPMENT.md) for more information on how to set up the development environment or the [justfile](justfile)  
 
🗓️ Last updated: 2025-08-25
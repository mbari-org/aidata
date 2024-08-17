[![MBARI](https://www.mbari.org/wp-content/uploads/2014/11/logo-mbari-3b.png)](http://www.mbari.org)
[![Python](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/downloads/)

*aidata* is a command line tool to do basic extract, transform, load and download operations
on AI data for a number of projects at MBARI that require detection, clustering or classification
workflows.
 
This supports loading [sdcat](https://github.com/mbari-org/sdcat) formatted output and downloads from [Tator](https://www.tatorapp.com/) and 
[Redis](https://redis.io) databases, although support for other data sources is also possible, e.g. [FathomNet](https://fathomnet.org/).
so we decided to keep the name generic.

This also supports loading media from a directory or URL, and transforming data into various 
formats for machine learning, e.g. COCO, CIFAR, or PASCAL VOC format.

## Installation 

### Create the Anaconda environment

The fastest way to get started is to use the Anaconda environment.  This will create a conda environment called *aidata*.
```shell
git clone http://github.com/mbari-org/aidata.git
cd aidata
conda env create 
conda activate aidata
export PYTHONPATH=$PWD
```

Then create a .env file with the following contents in the root directory of the project:
```shell
TATOR_TOKEN=your_api_token
REDIS_PASSWORD=your_redis_password
ENVIRONMENT=testing or production
```

A docker version is also available at mbari/aidata, but that is a WIP.

Full documentation is available at [https://docs.mbari.org/internal/ai/data](https://docs.mbari.org/internal/ai/data/). 

## Commands

* `python aidata download --help` -  Download data, such as images, boxes, into various formats for machine learning e,g, COCO, CIFAR, or PASCAL VOC format
* `python aidata load --help` -  Load data, such as images, boxes, and exemplars into either a Postgres or REDIS database
* `python aidata db --help` -  Commands related to database management
* `python aidata transform --help` - Commands related to transforming downloaded data
* `python aidata  -h` - Print help message and exit.
 
Source code is available at [github.com/mbari-org/aidata](https://github.com/mbari-org/aidata/). 

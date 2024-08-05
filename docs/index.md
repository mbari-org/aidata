---
description: aidata installation and usage
---
[![MBARI](https://www.mbari.org/wp-content/uploads/2014/11/logo-mbari-3b.png)](http://www.mbari.org) 
 
*aidata* is a command line tool to do basic extract, transform, load and download operations from
AI data for a number of projects at MBARI that require detection, clustering or classification.
This assumes that your project has been setup on the MBARI mantis server and that you have a valid
account and token for the Tator database.
 

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

### Set your Tator token in an environment variable *or* pass it as an option with --token

```
export TATOR_TOKEN=15afoobaryouraccesstoken
```

![ Image link ](./imgs/apitoken.png)


## Commands

* [`python aidata download --help` -  Download data, such as images, boxes, into various formats for machine learning e,g, COCO, CIFAR, or PASCAL VOC format](commands/download.md)
* [`python aidata load --help` -  Load data, such as images, boxes, and exemplars into either a Postgres or REDIS database](commands/load.md)
* [`python aidata db --help` -  Commands related to database management](commands/db.md)
* `aidata -h` - Print help message and exit.
 
Source code is available at [github.com/mbari-org/aidata](https://github.com/mbari-org/aidata/). 

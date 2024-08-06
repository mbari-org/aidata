[![MBARI](https://www.mbari.org/wp-content/uploads/2014/11/logo-mbari-3b.png)](http://www.mbari.org)
[![Python](https://img.shields.io/badge/language-Python-blue.svg)](https://www.python.org/downloads/)

*aidata* is a command line tool to do basic extract, transform, load and download operations
on AI data for a number of projects at MBARI that require detection, clustering or classification
workflows.
 
This supports loading [sdcat](https://github.com/mbari-org/sdcat) formatted output and downloads from [Tator](https://www.tatorapp.com/) databases, although
support for other data sources is also possible, e.g. [FathomNet](https://fathomnet.org/).
so we decided to keep the name generic.

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

A docker version is also available at mbari/aidata, but that is a WIP.

Full documentation is available at [https://docs.mbari.org/internal/ai/aidata/commands](https://docs.mbari.org/internal/ai/aidata/commands). 

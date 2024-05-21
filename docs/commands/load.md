# *dataai* Load Command

Images need to be loaded before [SDCAT](https://github.com/mbari-org/sdcat) formatted csv files, e.g. 

```text
python aidata load images --token $TATOR_TOKEN --config config/config_cfe.yml --input /Volumes/CFElab/2021-07-01/ --section 2021/07
```

### TIP
Add the --dry-run to load without actually loading
```text
python aidata load images  --token $TATOR_TOKEN --config config/config_cfe.yml --input /Volumes/CFElab/2021-07-01/ --dry-run --section 2021/07
```

then load the SDCAT csv files, e.g.

```text
python aidata load boxes --token $TATOR_TOKEN --config config/config_cfe.yml --input /Volumes/CFElab/2021-07-01/ --version Baseline
```

## 
Each command has a number of options.  For example, the `load` command has the following options:

```shell
Usage: aidata load boxes [OPTIONS]

  Load boxes from a directory with SDCAT formatted CSV files

Options:
  --token TEXT       [required]
  --config PATH      Path to a YAML file with project configuration
                     [required]
  --dry-run          Dry run, do not load data
  --version TEXT     Version to load data into. Default is 'Baseline'
  --input TEXT       input CSV file or path with CSV detection files to load
  --max-num INTEGER  Maximum number of images to load
  -h, --help         Show this message and exit.
```

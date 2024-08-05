# Load Command

Loading data is a two-step process.   You will need to have a valid Tator token to load data into the database
and a configuration file that describes the project and the location of the data on your local machine. 

##  A note on configuration files

Choose your configuration file for your project, e.g. `config/config_cfe.yml`. Adjust if needed, e.g. to point to the 
correct mount point for the data on your local machine. This is used to check the data before loading and  to 
create a correct URL for reference in the database.  For example, if you have a mount point for the CFE lab data 
on your local machine at `/Volumes/CFElab`, you would set the `host` parameter in the configuration file to the  
to the hostname of the machine where the data is stored, e.g. `mantis.shore.mbari.org`.

```yaml
mounts:
  - name: "image"
    path: "/Volumes/CFElab"
    host: "mantis.shore.mbari.org"
    ...
```


## Step 1. Load images
Images need to be loaded before [SDCAT](https://github.com/mbari-org/sdcat) formatted csv files can be loaded, e.g. 

```bash
python aidata load images --token $TATOR_TOKEN --config config/config_cfe.yml --input /Volumes/CFElab/2021-07-01/ --section 2021/07
```

!!! tip

    Use the `--dry-run` option to see what will be loaded without actually loading the data.
    ```text
    python aidata load images  --token $TATOR_TOKEN --config config/config_cfe.yml --input /Volumes/CFElab/2021-07-01/ --dry-run --section 2021/07
    ```

## Step 2. Load SDCAT formatted csv files 

```bash
python aidata load boxes --token $TATOR_TOKEN --config config/config_cfe.yml --input /Volumes/CFElab/2021-07-01/ --version Baseline
```

### Need help? Try the `--help` option
 

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

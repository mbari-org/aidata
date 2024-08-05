# Database Commands


Reset the REDIS database. This will delete all data in the database. This is useful for testing purposes, but also
for resetting the database to a known state. 

Each project has its own database, specified in the configuration file on a separate port. The configuration file is specified with the
`--config` option. The configuration file is a YAML file that contains the following information:

```yaml
redis:
  host: localhost
  port: 6379
  db: 0
```

Password is passed as an argument to the command. 
    
```shell
python -m aidata db reset --config aidata/config/config_uav.yml --redis-password <password>
``` 
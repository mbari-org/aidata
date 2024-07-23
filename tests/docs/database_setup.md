
# Setting up TATOR database

This will start a local instance of the TATOR database  

First checkout the 1.2.5 release of TATOR. This is the version that is currently supported by the tests.
It is a modified version that supports locally hosted images, video and caching.

```shell
git clone --recurse-submodules https://github.com/mbari-org/tator
git checkout 1.2.5
cd tator
cp example.env .env
```

Replace localhost with name of your machine running the TATOR database in the **.env** file, e.g.

```.env
MAIN_HOST=ada.local # replace with your machine name
```

Add your IP to the e.g. `../tests/config/config_cfe.yml` file.

```yaml
mounts:
  - name: "image"
    ...
    host: "134.89.113.216" # replace with your IP
```

Start the TATOR database and UI with the following command:

```shell
make tator
```


When this completes, you should see something like the following output:
```shell
[+] Running 15/15
 ⠿ Container ui                 Started                                                                                                                                                                                                                                                                                                                                                                                                                                    0.4s
 ⠿ Container postgis            Running                                                                                                                                                                                                                                                                                                                                                                                                                                    0.0s
 ⠿ Container postgis-cron       Started                                                                                                                                                                                                                                                                                                                                                                                                                                    1.6s
 ⠿ Container create-extensions  Started                                                                                                                                                                                                                                                                                                                                                                                                                                    1.7s
 ⠿ Container minio              Running                                                                                                                                                                                                                                                                                                                                                                                                                                    0.0s
 ⠿ Container redis              Running                                                                                                                                                                                                                                                                                                                                                                                                                                    0.0s
 ⠿ Container create-bucket      Started                                                                                                                                                                                                                                                                                                                                                                                                                                    1.1s
 ⠿ Container image-worker1      Started                                                                                                                                                                                                                                                                                                                                                                                                                                   1.1s
 ⠿ Container image-worker2      Started                                                                                                                                                                                                                                                                                                                                                                                                                                    1.1s
 ⠿ Container image-worker3      Started                                                                                                                                                                                                                                                                                                                                                                                                                                    1.1s
 ⠿ Container image-worker4      Started                                                                                                                                                                                                                                                                                                                                                                                                                       1.1s
 ⠿ Container image-worker5      Started                                                                                                                                                                                                                                                                                                                                                                                                                                                  1.3s
 ⠿ Container db-worker          Started                                                                                                                                                                                                                                                                                                                                                                                                                                    1.7s
 ⠿ Container transcode-worker   Started                                                                                                                                                                                                                                                                                                                                                                                                                                    1.5s
 ⠿ Container transcode          Started                                                                                                                                                                                                                                                                                                                                                                                                                                    1.1s
 ⠿ Container gunicorn           Running                                                                                                                                                                                                                                                                                                                                                                                                                                    0.0s
 ⠿ Container nginx-tator        Started                                                                                                                                                                                                                                                                                                                                                                                                                                    2.0s
 ⠿ Container gunicorn-cron      Started                                                                                                                                                                                                                                                                                                                                                                                                                                    1.9s
 ⠿ Container migrate            Started
 ```

Now that the containers are running, you can create a *superuser* to use for management of the database.  This is a one-time operation.

Create a superuser
```shell
cd tator && make superuser 
```
  
Open browser to your local tator instance and create a new (not superuser) user

[http://localhost:8080/registration](http://localhost:8080/registration)
 
Use that new user to login and create a new project that matches what is in your config.yaml file e.g. **90111-CFE** with no presets.

[http://localhost:8080/accounts/login](http://localhost:8080/accounts/login)

![tatornewproject](./imgs/newproject.png)

Create an API token for the admin user and set it in your environment along with the host and the project name, e.g.

![tatorAPItoken](./imgs/apitoken.png)

Set the environment variables for the API host, token, and project name, e.g.

```shell=
export TATOR_TOKEN=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpZCI6MzYsInVzZXJuYW1lIjoiYWRtaW4iLCJleHAiOjE
```
 
Create a new media type called **Image** and a new Localization type called **box**.



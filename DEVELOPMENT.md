# Test/Development Setup

Setup a development server to run tests on your local machine with the following steps.

# Requirements
- [Docker](https://docs.docker.com/get-docker/)
- [Just](https://github.com/casey/just)

# 1. Launch a Tator stack
Instructions are in [database_setup.md](docs/database_setup.md)
# 2. Setup the remaining services
This will setup the remaining services needed for development, including redix and the nginx server.
```shell
just setup-docker-dev
```
 
What you should see when you navigate to [http://localhost:8082/data](http://localhost:8082/data) is a list of images that are served from the `tests/data` directory. 
This is useful for testing the image serving capabilities of the module.  

![nginx_images](./docs/nginx_images.png)
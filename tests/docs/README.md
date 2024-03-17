# Tests

Setup a development server to run tests. For now, the tests are run on the local machine.
Installation instructions are in  [database_setup.md](database_setup.md)

# Setup

Launch Nginx to serve images
```shell
docker stop nginx_images
docker rm nginx_images
docker run -d -p 8082:8082  \
    -v $PWD/tests/data/:/data  \
    -v $PWD/tests/nginx.conf:/etc/nginx/conf.d/default.conf \
    --restart always  \
    --name nginx_images nginx:1.23.3
```

What you should see when you navigate to [http://localhost:8082/data](http://localhost:8082/data) is a list of images that are served from the `tests/data` directory. 
This is useful for testing the image serving capabilities of the module.  

![nginx_images](./imgs/nginx_images.png)
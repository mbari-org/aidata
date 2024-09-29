#!/usr/bin/env just --justfile

# Source the .env file
set dotenv-load := true

# List recipes
list:
    @just --list --unsorted

# Setup the environment
install:
    conda env create -f environment.yml
    python -m pip install --upgrade pip

# Update the environment. Run this command after checking out any code changes
update:
    conda env update --file environment.yml --prune

# Setup the docker development environment
setup-docker-dev:
    #!/usr/bin/env bash
    docker stop nginx_images
    docker rm nginx_images
    docker run -d -p 8082:8082  \
        -v $PWD/tests/data/:/data  \
        -v $PWD/tests/nginx.conf:/etc/nginx/conf.d/default.conf \
        --restart always  \
        --name nginx_images nginx:1.23.3
    docker volume create redis-test
    docker stop redis-test && docker rm redis-test || true
    docker run -d \
      --name redis-test \
      --env-file .env \
      -p 6379:6379 \
      -v redis-test:/var/lib/redis-stack \
      --restart always \
      redis/redis-stack-server \
      /bin/sh -c 'redis-stack-server --port 6382 --appendonly yes --appendfsync everysec --requirepass "${REDIS_PASSWD:?REDIS_PASSWD variable is not set}"'

# Test the media
test-load-media:
    #!/usr/bin/env bash
    export PYTHONPATH=.
    time conda run -n aidata --no-capture-output python3 tests/test_load_media.py

download-300m-data:
    #!/usr/bin/env bash
    export PYTHONPATH=.
    time conda run -n aidata --no-capture-output python3 aidata download dataset --base-path ./data/i2map --version Baseline --depth 300  --labels "all" --config ./aidata/config/config_i2map.yml

download-300m-data-gtp97:
    #!/usr/bin/env bash
    export PYTHONPATH=.
    time conda run -n aidata --no-capture-output python3 aidata download dataset --base-path ./data/i2map --version Baseline --depth 300  --min-score 0.97 --labels "all" --config ./aidata/config/config_i2map.yml

download-atolla-data:
    #!/usr/bin/env bash
    export PYTHONPATH=.
    time conda run -n aidata --no-capture-output python3 aidata download dataset --version Baseline --labels "Atolla" --cifar --cifar-size 128 --config ./aidata/config/config_bio.yml
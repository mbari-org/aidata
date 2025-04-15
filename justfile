#!/usr/bin/env just --justfile

# Source the .env file
set dotenv-load := true
set export

# Set the default shell to bash
set shell := ["bash", "-uc"]
CONDA_PREFIX := env("CONDA_PREFIX")

# Set the path to python envrionment
#env_dir := justfile_directory() / ".venv" / "bin" # uncomment if you are using a venv instead of conda
env_dir := CONDA_PREFIX / "bin"
# Uncomment the line below for cross-platform compatibility (Windows)
##export PATH := if os_family() == "windows" { env_dir + x";${PATH}" } else { env_dir + x":${PATH}" }
export PATH := env_dir + x":${PATH}"

# List recipes
list:
    @just --list --unsorted

# Build the docker images for linux/amd64 and linux/arm64 and push to Docker Hub
build-and-push:
    #!/bin/bash
    echo "Building and pushing the Docker image"
    RELEASE_VERSION=$(git describe --tags --abbrev=0)
    echo "Release version: $RELEASE_VERSION"
    RELEASE_VERSION=${RELEASE_VERSION:1}
    docker buildx create --name mybuilder --platform linux/amd64,linux/arm64 --use
    docker buildx build --sbom=true --provenance=true --push --platform linux/amd64,linux/arm64 -t mbari/aidata:$RELEASE_VERSION --build-arg IMAGE_URI=mbari/aidata:$RELEASE_VERSION -f docker/Dockerfile ..
    docker buildx build --sbom=true --provenance=true --push --platform linux/amd64 -t mbari/aidata:$RELEASE_VERSION-cuda124 --build-arg IMAGE_URI=mbari/aidata:$RELEASE_VERSION-cuda124 -f docker/Dockerfile.cuda ..

# Setup the environment
install:
    conda env create -f environment.yml
    python -m pip install --upgrade pip

# Update the environment. Run this command after checking out any code changes
update:
    conda env update --file environment.yml --prune

# Setup the database
setup-db:
    rm -rf tator
    git clone --recurse-submodules https://github.com/mbari-org/tator
    cd tator
    cp example-env .env
    make cluster
    make superuser

# TODO: Add a command to initialize the database from the yaml file
# See sightwire code for an example of how to do this
## Initialize the database
#init-db:
#    conda run -n mbari_aidata --no-capture-output python3 mbari_aidata db create

# Stop the docker development environment
stop-docker-dev:
    docker stop nginx_images
    docker stop redis-test
    cd tator && make clean && make tator

# Setup the docker development environment
setup-docker-dev:
    #!/bin/bash
    docker stop nginx_images
    docker rm nginx_images
    docker run -d -p 8082:8082  \
        -v $PWD/tests/data/:/data  \
        -v $PWD/tests/nginx.conf:/etc/nginx/conf.d/default.conf \
        --restart always  \
        --name nginx_images nginx:1.23.3
    # Get the IP address of the host and add it to the host: field in all the test yaml files
    export HOST_IP=$(ipconfig getifaddr en0)
    git checkout tests/config/*.yml
    sed -i '' "s/host: localhost/host: $HOST_IP/g" tests/config/*.yml
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
    cd tator && make tator


# Build the docker images for all platforms
build-docker:
    #!/bin/bash
    # Get the release version from the git tag and strip the v from the version
    export RELEASE_VERSION=$(git describe --tags --abbrev=0)
    export RELEASE_VERSION=${RELEASE_VERSION:1}
    echo "Building docker images for release version: $RELEASE_VERSION"
    docker buildx create --name mybuilder --platform linux/amd64,linux/arm64 --use
    docker buildx build --push --platform linux/amd64,linux/arm64 -t mbari/mbari_aidata:$RELEASE_VERSION --build-arg IMAGE_URI=mbari/mbari_aidata:$RELEASE_VERSION -f docker/Dockerfile .
    docker buildx build --push --platform linux/amd64 -t mbari/mbari_aidata:$RELEASE_VERSION-cuda124 --build-arg IMAGE_URI=mbari/mbari_aidata:$RELEASE_VERSION-cuda124 -f docker/Dockerfile.cuda .
    docker push mbari/mbari_aidata:$RELEASE_VERSION

# Install development dependencies. Run before running tests
install-dev:
    conda run -n mbari_aidata --no-capture-output python3 -m pip install -r requirements-dev.txt

# Load i2map images
load-i2map :
    time conda run -n mbari_aidata --no-capture-output python3 mbari_aidata load images \
        --config ./tests/config/config_i2map.yml \
        --input ./tests/data/i2map --token $TATOR_TOKEN

# Load cfe video
load-cfe:
    time conda run -n mbari_aidata --no-capture-output python3 mbari_aidata load videos \
        --config ./tests/config/config_cfe.yml \
        --input ./tests/data/cfe --token $TATOR_TOKEN

# Test loading of i2map images
test-load-i2map:
    time conda run -n mbari_aidata --no-capture-output pytest -r tests/test_load_media.py -k test_load_image_i2map

# Test loading of cfe images
test-load-cfe:
    time conda run -n mbari_aidata --no-capture-output pytest -r tests/test_load_media.py -k test_load_image_cfe

# Test dry-run loading of images or videos
test-dryrun:
    time conda run -n mbari_aidata --no-capture-output pytest -r tests/test_load_media.py -k test_load_image_dryrun
    time conda run -n mbari_aidata --no-capture-output pytest -r tests/test_load_media.py -k test_load_video_dryrun
# Download all verified data from the i2map project at 300m depth
download-300m-data:
    time conda run -n mbari_aidata --no-capture-output python3 mbari_aidata download dataset --base-path ./data/i2map --version Baseline --depth 300  --labels "all" --config config_i2map.yml
# Download all verified data from the i2map project at 300m depth with a minimum score of 0.97
download-300m-data-gtp97:
    time conda run -n mbari_aidata --no-capture-output python3 mbari_aidata download dataset --base-path ./data/i2map --version Baseline --depth 300  --min-score 0.97 --labels "all" --config config_i2map.yml
# Download the 300m data for the Atolla dataset with the mega-vits-track-gcam version
download-atolla-data:
    time conda run -n mbari_aidata --no-capture-output python3 mbari_aidata download dataset --voc --version mega-vits-track-gcam --labels "Atolla" --crop-roi --config config_bio.yml
# Download all verified data from the bio project and collapse the labels to a single class
download-single-class-data:
    time conda run -n mbari_aidata --no-capture-output python3 mbari_aidata download dataset --config --single-class "marineorganism" --version Baseline --labels "Atolla,Gymnopraia lapislazula" --voc  --config config_bio.yml
# Download the pinniped data from the UAV project
download-pinniped-data:
    time conda run -n mbari_aidata --no-capture-output python3 mbari_aidata download dataset --labels "Pinniped" --crop-roi --config config_uav.yml
download-jelly-data:
    time conda run -n mbari_aidata --no-capture-output python3 mbari_aidata download dataset --crop-roi --labels "Jelly" --config config_uav.yml
download-bird-data:
    time conda run -n mbari_aidata --no-capture-output python3 mbari_aidata download dataset --crop-roi --verified --labels "Bird" --config config_uav.yml
# Download the copepod data from the CFE project
download-copepod-data:
    time conda run -n mbari_aidata --no-capture-output python3 mbari_aidata download dataset --version Baseline --labels "copepod" --config config_cfe.yml
# Download the 25000_depth_v1 section data from the CFE project
download-section-data:
    time conda run -n mbari_aidata --no-capture-output python3 mbari_aidata download dataset --base-path ./data/i2map --version Baseline --section "25000_depth_v1"  --labels "all" --config config_cfe.yml
# Load the i2map data into redis
load-redis:
    time conda run -n mbari_aidata --no-capture-output python3 mbari_aidata load queue --reset \
        --config ./tests/config/config_cfe.yml \
        --token $TATOR_TOKEN
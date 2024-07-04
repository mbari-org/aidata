FROM python:3.11-alpine

# Install gcc and other build tools and libraries which are needed for dependencies
RUN apk --no-cache add git gcc python3-dev musl-dev linux-headers

LABEL vendor="MBARI"
LABEL maintainer="dcline@mbari.org"
LABEL license="Apache License 2.0"

ARG GH_TOKEN
ARG GIT_VERSION=latest
ARG IMAGE_URI=mbari/aidata:${GIT_VERSION}
ARG DOCKER_GID=1001
ARG DOCKER_UID=12065

# Create a user with a specific UID and GID.
RUN addgroup -g ${DOCKER_GID} docker && \
    adduser  -u ${DOCKER_UID} -G docker -D docker_user

# Install in the virtual environment as the docker user.
USER docker_user
WORKDIR /home/docker_user

# Create a virtual environment for the application dependencies.
ENV VIRTUAL_ENV=/home/docker_user/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"
ENV PYTHONPATH=/home/docker_user/aidata
RUN pip install --upgrade pip

RUN if [ "$GIT_VERSION" != "latest" ]; then \
    git clone -b v${GIT_VERSION} --depth 1 https://${GH_TOKEN}@github.com/mbari-org/aidata.git; \
    else \
    git clone --depth 1 https://${GH_TOKEN}@github.com/mbari-org/aidata.git;\
    fi

# Remove the configuration files
RUN rm -rf /home/docker_user/aidata/config/*

WORKDIR /home/docker_user/aidata
RUN pip install -r requirements.txt
ENTRYPOINT ["python", "aidata"]
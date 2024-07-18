FROM ubuntu:22.04

LABEL vendor="MBARI"
LABEL maintainer="dcline@mbari.org"
LABEL license="Apache License 2.0"

RUN apt-get update && apt-get install -y \
    software-properties-common \
    && apt-get update && apt-get install -y \
    python3.11 \
    python3.11-dev \
    python3.11-distutils \
    python3-pip \
    curl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

ARG GIT_VERSION=latest
ARG IMAGE_URI=mbari/aidata:${GIT_VERSION}

ENV APP_HOME /app
WORKDIR ${APP_HOME}
ADD . ${APP_HOME}
ENV PYTHONPATH=${APP_HOME}/aidata

RUN python3.11 -m pip install --upgrade pip && \
    python3.11 -m pip install -r requirements.txt
ENTRYPOINT ["python3.11", "aidata"]
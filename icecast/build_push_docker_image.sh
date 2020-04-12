#!/bin/bash

APP_NAME=icecast2
VERSION=2.4.4

docker build -t ${APP_NAME}:${VERSION} .
docker tag ${APP_NAME}:${VERSION} gcr.io/apoweroftrance/${APP_NAME}:${VERSION}
docker tag ${APP_NAME}:${VERSION} gcr.io/apoweroftrance/${APP_NAME}:latest
gcloud docker -- push gcr.io/apoweroftrance/${APP_NAME}:${VERSION}
gcloud docker -- push gcr.io/apoweroftrance/${APP_NAME}:latest
#!/bin/bash

APP_NAME=nginx
VERSION=1.17.10-r0

docker build --no-cache=True -t ${APP_NAME}:${VERSION} .
docker tag ${APP_NAME}:${VERSION} gcr.io/apoweroftrance/${APP_NAME}:${VERSION}
docker tag ${APP_NAME}:${VERSION} gcr.io/apoweroftrance/${APP_NAME}:latest
docker push gcr.io/apoweroftrance/${APP_NAME}:${VERSION}
docker push gcr.io/apoweroftrance/${APP_NAME}:latest


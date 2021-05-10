#!/bin/bash

APP_NAME=icecast2
VERSION=2.4.4

docker build --no-cache=True -t ${APP_NAME}:${VERSION} .
docker tag ${APP_NAME}:${VERSION} gcr.io/apoweroftrance/${APP_NAME}:${VERSION}
docker tag ${APP_NAME}:${VERSION} gcr.io/apoweroftrance/${APP_NAME}:latest
docker push gcr.io/apoweroftrance/${APP_NAME}:${VERSION}
docker push gcr.io/apoweroftrance/${APP_NAME}:latest


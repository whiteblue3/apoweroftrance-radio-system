#!/bin/bash

APP_NAME=radio
VERSION=0.0.83

docker build -t ${APP_NAME}:${VERSION} .
docker tag ${APP_NAME}:${VERSION} gcr.io/apoweroftrance/${APP_NAME}:${VERSION}
docker tag ${APP_NAME}:${VERSION} gcr.io/apoweroftrance/${APP_NAME}:production-${VERSION}
docker tag ${APP_NAME}:${VERSION} gcr.io/apoweroftrance/${APP_NAME}:latest
docker tag ${APP_NAME}:${VERSION} gcr.io/apoweroftrance/${APP_NAME}:production-latest
docker push gcr.io/apoweroftrance/${APP_NAME}:${VERSION}
docker push gcr.io/apoweroftrance/${APP_NAME}:production-${VERSION}
docker push gcr.io/apoweroftrance/${APP_NAME}:latest
docker push gcr.io/apoweroftrance/${APP_NAME}:production-latest
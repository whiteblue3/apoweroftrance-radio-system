#!/bin/bash

docker build -t django:2.2.12 .
docker tag django:2.2.12 gcr.io/apoweroftrance/django:2.2.12
gcloud docker -- push gcr.io/apoweroftrance/django:2.2.12

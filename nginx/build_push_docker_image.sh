#!/bin/bash

docker build -t nginx:1.17.9 .
docker tag nginx:1.17.9 gcr.io/apoweroftrance/nginx:1.17.9
gcloud docker -- push gcr.io/apoweroftrance/nginx:1.17.9

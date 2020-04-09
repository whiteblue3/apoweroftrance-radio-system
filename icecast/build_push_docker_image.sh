#!/bin/bash

docker build -t icecast2:2.4.4 .
docker tag icecast2:2.4.4 gcr.io/apoweroftrance/icecast2:2.4.4
gcloud docker -- push gcr.io/apoweroftrance/icecast2:2.4.4

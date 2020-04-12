#!/bin/bash
set -e

mkdir -p ${MOUNT_POINT}
chmod a+w ${MOUNT_POINT}

gcloud auth activate-service-account --key-file=${GOOGLE_APPLICATION_CREDENTIALS}
gcsfuse --key-file=${GOOGLE_APPLICATION_CREDENTIALS} --foreground -o allow_other -o rw --implicit-dirs ${BUCKET} ${MOUNT_POINT}

exec "$@"

FROM ubuntu:xenial

ENV MOUNT_POINT /mnt

# ignore when FUSE is none
ENV BUCKET ""

# using when FUSE is gcs
ENV GOOGLE_APPLICATION_CREDENTIALS /etc/gcloud/service-account-key.json

RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates wget \
  && echo "deb http://packages.cloud.google.com/apt cloud-sdk-xenial main" | tee /etc/apt/sources.list.d/google-cloud.sdk.list \
  && echo "deb http://packages.cloud.google.com/apt gcsfuse-xenial main" | tee /etc/apt/sources.list.d/gcsfuse.list \
  && wget -qO- https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add - \
  && apt-get update && apt-get install -y --no-install-recommends google-cloud-sdk gcsfuse \
  && rm -rf /var/lib/apt/lists

WORKDIR /etc/gcloud

VOLUME /mnt

COPY mount.sh /etc/gcloud

ENTRYPOINT ["/etc/gcloud/mount.sh"]
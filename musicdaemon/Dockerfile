FROM python:3.6-alpine

COPY . /daemon
WORKDIR /daemon

RUN mkdir -p /srv/media

VOLUME ["/srv/media"]
#COPY mpd.conf /etc/mpd.conf

RUN apk update && \
    apk add postgresql-libs && \
    apk add --virtual .build-deps gcc musl-dev postgresql-dev && \
    python3 -m pip install -r requirement.txt --no-cache-dir && \
    apk --purge del .build-deps

CMD ["python3", "main.py"]

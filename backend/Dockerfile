FROM python:3.6-slim

ENV PYTHONUNBUFFERED 0

#COPY . /backend
WORKDIR /backend

COPY ./startup.sh /backend/startup.sh

RUN apt-get -y update
RUN apt-get -y install --no-install-recommends build-essential vim \
    && apt-get purge -y --auto-remove \
    && rm -rf /var/lib/apt/lists/*

RUN python3 -m pip install --upgrade pip
RUN python3 -m pip install --no-cache-dir uwsgi==2.0.18

#RUN python3 -m pip install -r requirement.txt

RUN rm -f /var/cache/apt/archives/*.rpm /var/cache/apt/*.bin /var/lib/apt/lists/*.*;

RUN chmod a+x startup.sh

ENTRYPOINT ["/backend/startup.sh"]

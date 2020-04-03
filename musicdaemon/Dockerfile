FROM ubuntu:18.04

COPY . /daemon
WORKDIR /daemon

RUN mkdir -p /srv/media

VOLUME ["/srv/media"]
COPY config.ini ./config.ini

RUN apt-get -y update
RUN apt-get install -y python3.6 python3-pip software-properties-common libshout3

RUN python3 -m pip install -r requirement.txt

EXPOSE 9000

ENTRYPOINT ["python3", "main.py"]

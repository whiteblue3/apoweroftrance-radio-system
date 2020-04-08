FROM ubuntu:18.04

COPY . /daemon
WORKDIR /daemon

RUN mkdir -p /srv/media

VOLUME ["/srv/media"]
COPY config.ini ./config.ini

RUN apt-get -y update
RUN apt-get install -y python3.6 python3-pip software-properties-common libshout3-dev
#RUN python-setuptools build-essential git libvorbis-dev libogg-dev libfdk-aac-dev

#WORKDIR /root
#RUN git clone https://github.com/whiteblue3/libshout-aac.git
#WORKDIR /root/libshout-aac
#RUN ./configure
#RUN make
#RUN make install

WORKDIR /daemon
RUN python3 -m pip install -r requirement.txt

EXPOSE 9000

ENTRYPOINT ["python3", "main.py"]

FROM python:3.6-slim

ENV PYTHONUNBUFFERED 0

#COPY . /backend
WORKDIR /backend

COPY ./startup.sh /backend/startup.sh

RUN apt-get -y update
RUN apt-get -y install build-essential vim

RUN python3 -m pip install --upgrade pip
#RUN python3 -m pip install -r requirement.txt

RUN chmod a+x startup.sh

ENTRYPOINT ["/backend/startup.sh"]

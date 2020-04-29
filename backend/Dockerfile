FROM python:3.6-slim

ENV PYTHONUNBUFFERED 0

RUN mkdir /backend
WORKDIR /backend

RUN apt-get update && apt-get -y install --no-install-recommends build-essential vim gnupg curl \
    && rm -rf /var/lib/apt/lists/*

# Install gcloud.
RUN apt-get install --no-install-recommends -y apt-transport-https ca-certificates \
    && rm -rf /var/lib/apt/lists/*
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -
RUN apt-get update
RUN apt-get install --no-install-recommends -y google-cloud-sdk \
    && rm -rf /var/lib/apt/lists/*

RUN rm -f /var/cache/apt/archives/*.rpm /var/cache/apt/*.bin /var/lib/apt/lists/*.*;

ENV NGINX=127.0.0.1:80

ENV DJANGO_SETTINGS_MODULE=app.settings
ENV UWSGI_WSGI_FILE=/backend/app/wsgi.py
#ENV UWSGI_SOCKET=/backend/app.sock UWSGI_CHMOD_SOCKET=644
#ENV UWSGI_HTTP=0.0.0.0:8090
ENV UWSGI_SOCKET=0.0.0.0:8090 UWSGI_CHMOD_SOCKET=644
ENV UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy UWSGI_POST_BUFFERING=1
ENV UWSGI_MASTER=1 UWSGI_HTTP_AUTO_CHUNKED=1 UWSGI_HTTP_KEEPALIVE=1 UWSGI_PROCESS=4
ENV UWSGI_STATIC_MAP="/static/=/backend/.static/" UWSGI_STATIC_EXPIRES_URI="/static/.*\.[a-f0-9]{12,}\.(css|js|png|jpg|jpeg|gif|ico|woff|ttf|otf|svg|scss|map|txt) 315360000"
#ENV UWSGI_ROUTE_HOST="^(?!${NGINX}$) break:400"

EXPOSE 8090

ENV USER=ubuntu
RUN useradd -rm -d /home/${USER} -s /bin/bash --no-log-init ${USER}

RUN chown -R ${USER}:${USER} /backend

COPY ./startup.sh /backend/startup.sh
RUN chmod a+x /backend/startup.sh

RUN python3 -m pip install --upgrade pip \
    && python3 -m pip install uwsgi==2.0.18

ENV GOOGLE_APPLICATION_CREDENTIALS /etc/gcloud/service-account-key.json

RUN mkdir -p /etc/gcloud

# Uncomment when production
#COPY . /backend/
#RUN python3 -m pip install --no-cache-dir -r requirement.txt

RUN apt-get update && apt-get install netcat-openbsd -y

ENV DB_ENGINE 'django.db.backends.postgresql'
ENV DB_NAME 'postgres'
ENV DB_HOST '127.0.0.1'
ENV DB_USERNAME 'postgres'
ENV DB_PASSWORD ''
ENV DB_PORT 5432

ENV REDIS_URL "127.0.0.1"
ENV REDIS_PORT 6379
ENV REDIS_DB 0

USER ${USER}

ENTRYPOINT ["./startup.sh"]

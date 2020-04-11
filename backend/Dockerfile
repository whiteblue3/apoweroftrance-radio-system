FROM python:3.6-slim

ENV PYTHONUNBUFFERED 0

ARG USER=user
RUN groupadd -r ${USER} && useradd --no-log-init -r -g ${USER} ${USER}

RUN mkdir /backend
# Uncomment when production
#COPY --chown=${USER}:${USER} . /backend/
WORKDIR /backend

COPY --chown=${USER}:${USER} ./django_utils-0.0.1.tar.gz /backend/
COPY --chown=${USER}:${USER} ./accounts-0.0.1.tar.gz /backend/

COPY --chown=${USER}:${USER} ./requirement.txt /backend/
COPY --chown=${USER}:${USER} ./startup.sh /backend/

RUN apt-get -y update
RUN apt-get -y install --no-install-recommends build-essential vim \
    && rm -rf /var/lib/apt/lists/*

RUN rm -f /var/cache/apt/archives/*.rpm /var/cache/apt/*.bin /var/lib/apt/lists/*.*;

RUN python3 -m pip install --upgrade pip

ENV DJANGO_SETTINGS_MODULE=app.settings
ENV UWSGI_WSGI_FILE=/backend/app/wsgi.py
ENV UWSGI_SOCKET=/backend/app.sock UWSGI_CHMOD_SOCKET=644 UWSGI_MASTER=1 UWSGI_HTTP_AUTO_CHUNKED=1 UWSGI_HTTP_KEEPALIVE=1 UWSGI_LAZY_APPS=1 UWSGI_WSGI_ENV_BEHAVIOR=holy
ENV UWSGI_WORKERS=2 UWSGI_THREADS=4
ENV UWSGI_STATIC_MAP="/static/=/backend/.static/" UWSGI_STATIC_EXPIRES_URI="/static/.*\.[a-f0-9]{12,}\.(css|js|png|jpg|jpeg|gif|ico|woff|ttf|otf|svg|scss|map|txt) 315360000"
#ENV UWSGI_ROUTE_HOST="^(?!10.0.0.4:8080$) break:400"

# Uncomment when production
#RUN python3 -m pip install --no-cache-dir -r requirement.txt

RUN chmod a+x startup.sh

CMD ["/backend/startup.sh"]

#USER ${USER}:${USER}
#ENTRYPOINT ["/bin/bash"]
FROM nginx:latest

ARG USER=appuser
RUN groupadd -r ${USER} && useradd --no-log-init -r -g ${USER} ${USER}

RUN apt-get -y update
RUN apt-get -y install --no-install-recommends nginx-extras vim \
    && rm -rf /var/lib/apt/lists/*

RUN rm -f /var/cache/apt/archives/*.rpm /var/cache/apt/*.bin /var/lib/apt/lists/*.*;

EXPOSE 80

USER ${USER}:${USER}

CMD ["nginx", "-g", "daemon off;"]

FROM nginx:latest

RUN apt-get -y update
RUN apt-get -y install --no-install-recommends nginx-extras \
    && rm -rf /var/lib/apt/lists/*

RUN rm -f /var/cache/apt/archives/*.rpm /var/cache/apt/*.bin /var/lib/apt/lists/*.*;

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]

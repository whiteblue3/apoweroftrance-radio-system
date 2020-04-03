FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 0

COPY . /backend
WORKDIR /backend

COPY accounts-0.0.1.tar.gz /backend/accounts-0.0.1.tar.gz
COPY django_utils-0.0.1.tar.gz /backend/django_utils-0.0.1.tar.gz

RUN apk update && \
    apk add postgresql-libs && \
    apk add --virtual .build-deps gcc musl-dev postgresql-dev && \
    python3 -m pip install -r requirement.txt --no-cache-dir && \
    apk --purge del .build-deps

EXPOSE 8080

RUN chmod +x startup.sh

ENTRYPOINT ["/backend/startup.sh"]
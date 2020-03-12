FROM python:3.6-alpine

ENV PYTHONUNBUFFERED 0

COPY . /backend

RUN apk update && \
    apk add postgresql-libs && \
    apk add --virtual .build-deps gcc musl-dev postgresql-dev && \
    python3 -m pip install -r /backend/requirement.txt --no-cache-dir && \
    apk --purge del .build-deps

WORKDIR /backend
EXPOSE 8080

ENTRYPOINT ["python3", "manage.py", "collectstatic", "--noinput", "-i yes"]
ENTRYPOINT ["python3", "manage.py", "makemigrations"]
ENTRYPOINT ["python3", "manage.py", "migrate"]

ENTRYPOINT ["python3", "manage.py", "runserver", "0.0.0.0:8080"]
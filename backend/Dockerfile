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

#ADD https://raw.githubusercontent.com/vishnubob/wait-for-it/master/wait-for-it.sh .

#RUN chmod +x wait-for-it.sh
RUN chmod +x startup.sh

#ENTRYPOINT ["python3", "manage.py", "collectstatic", "--noinput", "-i yes"]
#ENTRYPOINT ["python3", "manage.py", "makemigrations", "--noinput"]
#ENTRYPOINT ["python3", "manage.py", "migrate", "--noinput"]
#
#ENTRYPOINT ["python3", "manage.py", "runserver", "0.0.0.0:8080"]

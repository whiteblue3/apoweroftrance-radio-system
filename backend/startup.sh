#!/bin/sh

python3 manage.py collectstatic --noinput -i yes
python3 manage.py makemigrations --noinput
python3 manage.py migrate --noinput

python3 manage.py runserver 0.0.0.0:8080
exec "$@"
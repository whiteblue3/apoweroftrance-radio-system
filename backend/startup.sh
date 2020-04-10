#!/bin/sh

python3 -m pip install -r requirement.txt

python3 manage.py collectstatic --noinput -i yes
python3 manage.py migrate --noinput
python3 manage.py makemigrations accounts
python3 manage.py makemigrations radio
python3 manage.py migrate

uwsgi --ini uwsgi.ini

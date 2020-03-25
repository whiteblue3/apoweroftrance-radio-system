#!/bin/sh

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd ${SCRIPTDIR}/django-utils/
python3 setup.py sdist bdist_wheel
cp ${SCRIPTDIR}/django-utils/dist/django_utils-0.0.1.tar.gz ${SCRIPTDIR}/backend/
#python3 -m pip install ${SCRIPTDIR}/backend/django_utils-0.0.1.tar.gz

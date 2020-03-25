#!/bin/sh

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd ${SCRIPTDIR}/django-accounts/
python3 setup.py sdist bdist_wheel
cp ${SCRIPTDIR}/django-accounts/dist/accounts-0.0.1.tar.gz ${SCRIPTDIR}/backend/
#python3 -m pip install ${SCRIPTDIR}/backend/accounts-0.0.1.tar.gz
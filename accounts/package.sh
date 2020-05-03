#!/bin/sh

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VERSION=0.0.1

cd ${SCRIPTDIR}/accounts/
python3 setup.py sdist bdist_wheel
cp ${SCRIPTDIR}/accounts/dist/accounts-${VERSION}.tar.gz ${SCRIPTDIR}/backend/
python3 -m pip install ${SCRIPTDIR}/backend/accounts-${VERSION}.tar.gz

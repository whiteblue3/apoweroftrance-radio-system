#!/bin/sh

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VERSION=0.0.1

cd ${SCRIPTDIR}/backend/
python3 setup.py sdist bdist_wheel
cp ${SCRIPTDIR}/backend/dist/apoweroftrance-backend-${VERSION}.tar.gz ${SCRIPTDIR}/admin/
python3 -m pip install ${SCRIPTDIR}/admin/apoweroftrance-backend-${VERSION}.tar.gz

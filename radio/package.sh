#!/bin/sh

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VERSION=0.0.1

cd ${SCRIPTDIR}/radio/
python3 setup.py sdist bdist_wheel
cp ${SCRIPTDIR}/radio/dist/apoweroftrance-radio-${VERSION}.tar.gz ${SCRIPTDIR}/upload/
cp ${SCRIPTDIR}/radio/dist/apoweroftrance-radio-${VERSION}.tar.gz ${SCRIPTDIR}/post/
cp ${SCRIPTDIR}/radio/dist/apoweroftrance-radio-${VERSION}.tar.gz ${SCRIPTDIR}/admin/
python3 -m pip install ${SCRIPTDIR}/upload/apoweroftrance-radio-${VERSION}.tar.gz
python3 -m pip install ${SCRIPTDIR}/post/apoweroftrance-radio-${VERSION}.tar.gz
python3 -m pip install ${SCRIPTDIR}/admin/apoweroftrance-radio-${VERSION}.tar.gz

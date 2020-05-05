#!/bin/sh

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VERSION=0.0.1

cd ${SCRIPTDIR}/account/
python3 setup.py sdist bdist_wheel
cp ${SCRIPTDIR}/account/dist/apoweroftrance-account-${VERSION}.tar.gz ${SCRIPTDIR}/radio/
#python3 -m pip install ${SCRIPTDIR}/radio/apoweroftrance-account-${VERSION}.tar.gz


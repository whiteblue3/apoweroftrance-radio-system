#!/bin/sh

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VERSION=0.0.1

cd ${SCRIPTDIR}/account/
python3 setup.py sdist bdist_wheel
cp ${SCRIPTDIR}/account/dist/apoweroftrance-account-${VERSION}.tar.gz ${SCRIPTDIR}/radio/
cp ${SCRIPTDIR}/account/dist/apoweroftrance-account-${VERSION}.tar.gz ${SCRIPTDIR}/upload/
#cp ${SCRIPTDIR}/account/dist/apoweroftrance-account-${VERSION}.tar.gz ${SCRIPTDIR}/../cms/
cp ${SCRIPTDIR}/account/dist/apoweroftrance-account-${VERSION}.tar.gz ${SCRIPTDIR}/post/
cp ${SCRIPTDIR}/account/dist/apoweroftrance-account-${VERSION}.tar.gz ${SCRIPTDIR}/admin/
#python3 -m pip install ${SCRIPTDIR}/radio/apoweroftrance-account-${VERSION}.tar.gz
#python3 -m pip install ${SCRIPTDIR}/upload/apoweroftrance-account-${VERSION}.tar.gz
#python3 -m pip install ${SCRIPTDIR}/post/apoweroftrance-account-${VERSION}.tar.gz
#python3 -m pip install ${SCRIPTDIR}/admin/apoweroftrance-account-${VERSION}.tar.gz
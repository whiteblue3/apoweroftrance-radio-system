#!/bin/sh

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VERSION=0.0.1

cd ${SCRIPTDIR}/post/
python3 setup.py sdist bdist_wheel
cp ${SCRIPTDIR}/post/dist/apoweroftrance-post-${VERSION}.tar.gz ${SCRIPTDIR}/admin/
python3 -m pip install ${SCRIPTDIR}/admin/apoweroftrance-post-${VERSION}.tar.gz

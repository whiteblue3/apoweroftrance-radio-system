#!/bin/sh

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VERSION=0.0.1

cd ${SCRIPTDIR}/django-utils/
python3 setup.py sdist bdist_wheel
cp ${SCRIPTDIR}/django-utils/dist/apoweroftrance-django-utils-${VERSION}.tar.gz ${SCRIPTDIR}/radio/
cp ${SCRIPTDIR}/django-utils/dist/apoweroftrance-django-utils-${VERSION}.tar.gz ${SCRIPTDIR}/account/
cp ${SCRIPTDIR}/django-utils/dist/apoweroftrance-django-utils-${VERSION}.tar.gz ${SCRIPTDIR}/upload/
cp ${SCRIPTDIR}/django-utils/dist/apoweroftrance-django-utils-${VERSION}.tar.gz ${SCRIPTDIR}/post/
cp ${SCRIPTDIR}/django-utils/dist/apoweroftrance-django-utils-${VERSION}.tar.gz ${SCRIPTDIR}/admin/
cp ${SCRIPTDIR}/django-utils/dist/apoweroftrance-django-utils-${VERSION}.tar.gz ${SCRIPTDIR}/../cms/
#python3 -m pip install ${SCRIPTDIR}/radio/apoweroftrance-django-utils-${VERSION}.tar.gz
#python3 -m pip install ${SCRIPTDIR}/account/apoweroftrance-django-utils-${VERSION}.tar.gz
#python3 -m pip install ${SCRIPTDIR}/upload/apoweroftrance-django-utils-${VERSION}.tar.gz
#python3 -m pip install ${SCRIPTDIR}/post/apoweroftrance-django-utils-${VERSION}.tar.gz
#python3 -m pip install ${SCRIPTDIR}/admin/apoweroftrance-django-utils-${VERSION}.tar.gz

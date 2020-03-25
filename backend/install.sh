#!/bin/sh

SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

python3 -m pip install ${SCRIPTDIR}/backend/accounts-0.0.1.tar.gz
python3 -m pip install ${SCRIPTDIR}/backend/django_utils-0.0.1.tar.gz

#!/bin/bash

set -e
set -u

if [ -n "$POSTGRES_MULTIPLE_DB" ]; then
	for dbname in $(echo $POSTGRES_MULTIPLE_DB | tr ',' ' '); do
	psql --username "$POSTGRES_USER" <<-EOSQL
	    CREATE DATABASE "$dbname";
	    GRANT ALL PRIVILEGES ON DATABASE "$dbname" TO "$POSTGRES_USER";
EOSQL
	done
fi

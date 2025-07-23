#!/bin/bash

set -e

host="$1"
database="$2"
user="$3"
password="$4"
shift


echo "host=$host database=$database username=$user password=$password"
until PGPASSWORD=$password psql -h "$host" -U $user -d $database -P "pager=off" -c '\l'; do
  >&2 echo "${GEONODE_DATABASE} is unavailable - sleeping"
  sleep 1
done

>&2 echo "Database are up - executing command"
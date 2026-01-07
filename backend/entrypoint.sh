#!/bin/bash

# Fail if a command fails
set -e

# Run migrations
poetry run python manage.py makemigrations --noinput
poetry run python manage.py migrate --noinput
poetry run python manage.py collectstatic --noinput

# Run the ASGI server
exec "$@"

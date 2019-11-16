#!/bin/sh
# This script is used to bot a Docker container
. venv/bin/activate
exec gunicorn -b :5000 --access-logfile - --error-logfile - run:app
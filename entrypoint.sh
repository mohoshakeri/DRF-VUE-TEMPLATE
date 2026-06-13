#!/usr/bin/env bash

# Create Logs Directories
mkdir -p /var/log/project

# Run Migrations
python manage.py migrate --skip-checks
python manage.py collectstatic --no-input --skip-checks

# Execute Passed Command
exec "$@"

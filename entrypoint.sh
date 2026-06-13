#!/usr/bin/env bash

# Create Logs Directories
mkdir -p /var/log/xxx

# Run Migrations
python manage.py migrate --skip-checks
python manage.py collectstatic --no-input --skip-checks

# Execute Passed Command
exec "$@"

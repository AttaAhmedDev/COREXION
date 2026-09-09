#!/bin/sh
set -e
python manage.py load_cms_seed
exec gunicorn config.wsgi:application --bind "0.0.0.0:${PORT}"

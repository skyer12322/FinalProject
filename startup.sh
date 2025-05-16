#!/bin/bash
export DJANGO_SETTINGS_MODULE="myproject.settings.prod"
python manage.py collectstatic
daphne -b 0.0.0.0 -p 10000 FinalProject.asgi:application
#!/bin/bash
export DJANGO_SETTINGS_MODULE=FinalProject.settings.prod
python manage.py collectstatic --noinput --settings=FinalProject.settings.prod
daphne -b 0.0.0.0 -p 10000 FinalProject.asgi:application
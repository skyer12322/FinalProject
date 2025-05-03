#!/bin/bash
python manage.py collectstatic --noinput
daphne FinalProject.asgi:application --port 10000
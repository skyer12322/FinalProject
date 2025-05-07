#!/bin/bash
python manage.py collectstatic --noinput
daphne -b 0.0.0.0 -p 10000 FinalProject.asgi:application
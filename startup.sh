#!/bin/bash
python manage.py makemigrations RecruitHelper --empty
python manage.py makemigrations
python manage.py migrate
python manage.py runserver 0.0.0.0:10000
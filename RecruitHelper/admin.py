"""
Модуль для настройки административной панели Django.
"""
from django.contrib import admin
from .models import Vacancy

admin.site.register(Vacancy)

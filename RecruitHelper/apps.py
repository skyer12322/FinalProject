"""
Модуль конфигурации приложения RecruitHelper.
"""
from django.apps import AppConfig

class RecruithelperConfig(AppConfig):
    """
    Класс конфигурации приложения RecruitHelper.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'RecruitHelper'

    def ready(self):
        import RecruitHelper.cache_utils

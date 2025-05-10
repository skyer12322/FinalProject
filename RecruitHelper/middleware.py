"""
Модуль с промежуточным ПО (middleware) для приложения.
"""
from django.utils.deprecation import MiddlewareMixin
from .storage import local_storage

class RequestMiddleware(MiddlewareMixin):
    """
    Пользовательское промежуточное ПО для обработки запросов.
    """
    def process_request(self, request):
        """
        Обработка запроса
        """
        local_storage.request = request
    def additiona_method(self):
        """
        Дополнительная функция
        """
        return 0

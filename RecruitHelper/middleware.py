from django.utils.deprecation import MiddlewareMixin
from .storage import local_storage  # Импорт из общего модуля

class RequestMiddleware(MiddlewareMixin):
    def process_request(self, request):
        local_storage.request = request
import logging
from .storage import local_storage  # Импорт из общего модуля

class UserIDFilter(logging.Filter):
    def filter(self, record):
        request = getattr(local_storage, 'request', None)
        
        user_id = 'anonymous'
        if request:
            try:
                if request.user.is_authenticated:
                    user_id = request.user.id
                else:
                    user_id = 'none'
            except AttributeError:
                user_id = 'no-user-model'
        
        record.user_id = user_id
        return True
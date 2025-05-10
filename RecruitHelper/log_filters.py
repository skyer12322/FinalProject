"""
Модуль с фильтрами для логирования.
"""
import logging
from .storage import local_storage

class UserIDFilter(logging.Filter):
    """
    Фильтр логирования для добавления ID пользователя к каждой записи лога.
    """
    def filter(self, record):
        """
        Добавляет атрибут user_id к записи лога.

        Определяет ID пользователя из объекта запроса, если доступно.
        :param record: Объект записи лога.
        :return: True, чтобы запись была обработана дальше.
        """
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

    def additional_method(self):
        """
        Дополнительная функция
        """
        return 0

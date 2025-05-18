"""
Модуль с тестами для фильтров логирования.
"""
import pytest
import logging
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from RecruitHelper.log_filters import UserIDFilter
from RecruitHelper.models import User
from RecruitHelper.storage import local_storage

@pytest.fixture
def log_filter():
    """
    Фикстура для фильтра логирования
    """
    return UserIDFilter()

@pytest.fixture
def log_record():
    """
    Фикстура для записи лога
    """
    record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_path",
        lineno=42,
        msg="Test message",
        args=(),
        exc_info=None
    )
    return record

def test_filter_anonymous(log_filter, log_record):
    """
    Тест фильтра для анонимного пользователя
    """
    # Очистка атрибута request, если он существует
    if hasattr(local_storage, 'request'):
        delattr(local_storage, 'request')
    
    assert log_filter.filter(log_record) is True
    assert log_record.user_id == 'anonymous'

def test_filter_authenticated_user(log_filter, log_record):
    """
    Тест фильтра для аутентифицированного пользователя
    """
    request = RequestFactory().get('/')
    class MockUser:
        @property
        def is_authenticated(self):
            return True
        id = 42
    
    user = MockUser()
    request.user = user
    
    local_storage.request = request
    
    assert log_filter.filter(log_record) is True
    assert log_record.user_id == 42

def test_filter_unauthenticated_user(log_filter, log_record):
    """
    Тест фильтра для неаутентифицированного пользователя
    """
    request = RequestFactory().get('/')
    request.user = AnonymousUser()
    
    local_storage.request = request
    
    assert log_filter.filter(log_record) is True
    assert log_record.user_id == 'none'

def test_filter_no_user_model(log_filter, log_record):
    """
    Тест фильтра при отсутствии модели пользователя
    """
    request = RequestFactory().get('/')
    # Не устанавливаем атрибут user
    
    local_storage.request = request
    
    assert log_filter.filter(log_record) is True
    assert log_record.user_id == 'no-user-model'

def test_additional_method(log_filter):
    """
    Тест дополнительного метода фильтра
    """
    assert log_filter.additional_method() == 0
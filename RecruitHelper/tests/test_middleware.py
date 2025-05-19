"""
Модуль с тестами для middleware.
"""
import pytest
from django.test import RequestFactory
from RecruitHelper.middleware import RequestMiddleware
from RecruitHelper.storage import local_storage

def test_process_request():
    """
    Тест обработки запроса middleware
    """
    middleware = RequestMiddleware(get_response=lambda r: None)
    request = RequestFactory().get('/')
    middleware.process_request(request)
    assert hasattr(local_storage, 'request')
    assert local_storage.request == request

def test_additional_method():
    """
    Тест дополнительного метода middleware
    """
    middleware = RequestMiddleware(get_response=lambda r: None)
    assert middleware.additiona_method() == 0
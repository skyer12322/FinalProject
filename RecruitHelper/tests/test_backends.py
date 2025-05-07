"""
Модуль с тестами для бэкендов аутентификации.
"""
import pytest
from RecruitHelper.backends import UserAuthBackend
from RecruitHelper.models import User, Company, CUser

pytestmark = pytest.mark.django_db

@pytest.fixture
def backend():
    """
    Фикстура бэкенда авторизации
    """
    return UserAuthBackend()

@pytest.fixture
def user():
    """
    Фикстура пользователя
    """
    u = User.objects.create_user(email='u@u.com', password='123', main_name='U')
    CUser.objects.create(user=u, first_name='F', last_name='L')
    return u

@pytest.fixture
def company():
    """
    Фикстура компании
    """
    u = User.objects.create_user(email='c@c.com', password='123', main_name='C', role='company')
    Company.objects.create(user=u)
    return u

def test_authenticate_by_email_and_main_name(backend, user):
    """
    Тест аутентификации пользователя по email и по main_name
    """
    assert backend.authenticate(None, email='u@u.com', password='123') == user
    # По main_name
    assert backend.authenticate(None, email='U', password='123') == user

def test_authenticate_wrong_password(backend):
    """
    Тест аутентификации при неправильном пароле
    """
    assert backend.authenticate(None, email='u@u.com', password='wrong') is None

def test_authenticate_company_check(backend, company):
    """
    Тест проверки на то, аутентифицируется компания или пользователь
    """
    assert backend.authenticate(None,
                                email='c@c.com',
                                password='123',
                                check_company=True) == company
    assert backend.authenticate(None, email='u@u.com', password='123', check_company=True) is None

def test_get_user(backend, user):
    """
    Тест получения пользователя / компании
    """
    assert backend.get_user(user.id) == user
    assert backend.get_user(99999) is None

import pytest
from RecruitHelper.backends import UserAuthBackend
from RecruitHelper.models import User, Company, CUser

pytestmark = pytest.mark.django_db

@pytest.fixture
def backend():
    return UserAuthBackend()

@pytest.fixture
def user():
    u = User.objects.create_user(email='u@u.com', password='123', main_name='U')
    CUser.objects.create(user=u, first_name='F', last_name='L')
    return u

@pytest.fixture
def company():
    u = User.objects.create_user(email='c@c.com', password='123', main_name='C', role='company')
    Company.objects.create(user=u)
    return u

def test_authenticate_by_email_and_main_name(backend, user):
    assert backend.authenticate(None, email='u@u.com', password='123') == user
    # По main_name
    assert backend.authenticate(None, email='U', password='123') == user

def test_authenticate_wrong_password(backend, user):
    assert backend.authenticate(None, email='u@u.com', password='wrong') is None

def test_authenticate_company_check(backend, company, user):
    # company, check_company=True
    assert backend.authenticate(None, email='c@c.com', password='123', check_company=True) == company
    # user, check_company=True
    assert backend.authenticate(None, email='u@u.com', password='123', check_company=True) is None

def test_get_user(backend, user):
    assert backend.get_user(user.id) == user
    assert backend.get_user(99999) is None

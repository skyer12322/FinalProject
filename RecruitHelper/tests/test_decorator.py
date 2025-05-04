import pytest
from django.test import RequestFactory
from django.contrib.auth.models import AnonymousUser
from RecruitHelper.models import User, Company, CUser
from RecruitHelper.decorators import anonymous_required, company_required, user_required

pytestmark = pytest.mark.django_db

def dummy_view(request):
    return 'ok'

def test_anonymous_required_redirect():
    rf = RequestFactory()
    user = User.objects.create_user(email='a@a.com', password='pass', main_name='A')
    request = rf.get('/')
    request.user = user
    resp = anonymous_required(dummy_view)(request)
    assert resp.status_code == 302

def test_anonymous_required_allowed():
    rf = RequestFactory()
    request = rf.get('/')
    request.user = AnonymousUser()
    assert anonymous_required(dummy_view)(request) == 'ok'

def test_company_required():
    rf = RequestFactory()
    user = User.objects.create_user(email='c@c.com', password='pass', main_name='C', role='company')
    Company.objects.create(user=user)
    request = rf.get('/')
    request.user = user
    assert company_required(dummy_view)(request) == 'ok'

def test_user_required():
    rf = RequestFactory()
    user = User.objects.create_user(email='u@u.com', password='pass', main_name='U')
    CUser.objects.create(user=user, first_name='F', last_name='L')
    request = rf.get('/')
    request.user = user
    assert user_required(dummy_view)(request) == 'ok'

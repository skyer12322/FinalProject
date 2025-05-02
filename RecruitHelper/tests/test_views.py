import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from RecruitHelper.models import User, Company, CUser, Vacancy, Application
from unittest.mock import patch

pytestmark = pytest.mark.django_db

@pytest.fixture
def client():
    from django.test import Client
    return Client()

@pytest.fixture
def user():
    user = User.objects.create_user(email='user@test.com', password='testpass', main_name='User')
    CUser.objects.create(user=user, first_name='Test', last_name='User')
    return user

@pytest.fixture
def company():
    user = User.objects.create_user(email='company@test.com', password='testpass', main_name='Company', role='company')
    Company.objects.create(user=user)
    return user

def test_home_view(client):
    resp = client.get(reverse('home'))
    assert resp.status_code == 200

def test_login_view_get(client):
    resp = client.get(reverse('login'))
    assert resp.status_code == 200

def test_login_view_post_fail(client):
    resp = client.post(reverse('login'), {'username': 'no@no.com', 'password': 'wrong'})
    assert resp.status_code == 200
    assert "Неверный email или пароль" in resp.content.decode()

def test_register_get(client):
    resp = client.get(reverse('register'))
    assert resp.status_code == 200

def test_register_post_user(client):
    resp = client.post(reverse('register'), {
        'main_name': 'User', 'email': 'u1@u.com', 'password': '123'
    })
    assert resp.status_code in (302, 200)

def test_logout_view(client, user):
    client.force_login(user)
    resp = client.get(reverse('logout'))
    assert resp.status_code == 302

def test_profile_view(client, user):
    client.force_login(user)
    resp = client.get(reverse('profile'))
    assert resp.status_code == 200

def test_edit_user_get(client, user):
    client.force_login(user)
    resp = client.get(reverse('edit_user'))
    assert resp.status_code == 200

def test_applications_user(client, user):
    client.force_login(user)
    resp = client.get(reverse('applications'))
    assert resp.status_code == 200

def test_company_view(client, company):
    resp = client.get(reverse('company', kwargs={'company_id': company.company.id}))
    assert resp.status_code == 200

def test_candidate_view(client, user):
    resp = client.get(reverse('candidate', kwargs={'user_id': user.id}))
    assert resp.status_code == 200

def test_vacancies_get(client):
    resp = client.get(reverse('vacancies_list'))
    assert resp.status_code == 200

@patch('RecruitHelper.views.ChatGPT.get_response')
def test_add_vacancy_post(mock_gpt, client, company):
    client.force_login(company)
    mock_gpt.return_value = {'rating': 5, 'tags': []}
    resp = client.post(reverse('add_vacancy'), {
        'title': 'Test', 'geography': 'City', 'description': 'Desc'
    })
    assert resp.status_code in (302, 200)

def test_vacancy_detail(client, user):
    vac = Vacancy.objects.create(title='T', description='D', geography={}, ai_rating=1)
    client.force_login(user)
    resp = client.get(reverse('vacancy', kwargs={'vacancy_id': vac.id}))
    assert resp.status_code == 200

@patch('RecruitHelper.views.ChatGPT.get_response')
def test_apply_to_vacancy(mock_gpt, client, user):
    vac = Vacancy.objects.create(title='T', description='D', geography={}, ai_rating=1)
    client.force_login(user)
    mock_gpt.return_value = '{"rating": 1}'
    resp = client.get(reverse('apply_to_vacancy', kwargs={'vacancy_id': vac.id}))
    assert resp.status_code in (302, 200)

def test_privacy_news_about(client):
    assert client.get(reverse('privacy')).status_code == 200
    assert client.get(reverse('news')).status_code == 200
    assert client.get(reverse('about_us')).status_code == 200

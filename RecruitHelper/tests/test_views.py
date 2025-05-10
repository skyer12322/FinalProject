"""
Модуль с тестами для представлений (views).
"""
from unittest.mock import patch
import pytest
from django.urls import reverse
from django.test import Client
from RecruitHelper.models import User, Company, CUser, Vacancy

pytestmark = pytest.mark.django_db

@pytest.fixture
def client():
    """Фикстура для тестового клиента."""
    return Client()

@pytest.fixture
def user():
    """Фикстура для создания тестового пользователя."""
    user_obj = User.objects.create_user(email='user@test.com',
                                        password='testpass',
                                        main_name='User')
    CUser.objects.create(user=user_obj, first_name='Test', last_name='User')
    return user_obj

@pytest.fixture
def company():
    """Фикстура для создания тестовой компании."""
    company_user = User.objects.create_user(email='company@test.com',
                                    password='testpass',
                                    main_name='Company',
                                    role='company')
    Company.objects.create(user=company_user)
    return company_user

def test_home_view(client):
    """Тест представления главной страницы."""
    resp = client.get(reverse('home'))
    assert resp.status_code == 200

def test_login_view_get(client):
    """Тест GET-запроса к представлению логина."""
    resp = client.get(reverse('login'))
    assert resp.status_code == 200

def test_login_view_post_fail(client):
    """Тест неудачного POST-запроса к представлению логина."""
    resp = client.post(reverse('login'), {'username': 'no@no.com', 'password': 'wrong'})
    assert resp.status_code == 200
    assert "Неверный email или пароль" in resp.content.decode()

def test_register_get(client):
    """Тест GET-запроса к представлению регистрации."""
    resp = client.get(reverse('register'))
    assert resp.status_code == 200

def test_register_post_user(client):
    """Тест POST-запроса для регистрации пользователя."""
    resp = client.post(reverse('register'), {
        'main_name': 'User', 'email': 'u1@u.com', 'password': '123'
    })
    assert resp.status_code in (302, 200)

def test_logout_view(client, user):
    """Тест представления выхода из системы."""
    client.force_login(user)
    resp = client.get(reverse('logout'))
    assert resp.status_code == 302

def test_profile_view(client, user):
    """Тест представления профиля пользователя."""
    client.force_login(user)
    resp = client.get(reverse('profile'))
    assert resp.status_code == 200

def test_edit_user_get(client, user):
    """Тест GET-запроса к представлению редактирования пользователя."""
    client.force_login(user)
    resp = client.get(reverse('edit_user'))
    assert resp.status_code == 200

def test_applications_user(client, user):
    """Тест представления списка заявок пользователя."""
    client.force_login(user)
    resp = client.get(reverse('applications'))
    assert resp.status_code == 200

def test_company_view(client, company):
    """Тест представления страницы компании."""
    resp = client.get(reverse('company', kwargs={'company_id': company.company.id}))
    assert resp.status_code == 200

def test_candidate_view(client, user):
    """Тест представления страницы кандидата."""
    resp = client.get(reverse('candidate', kwargs={'user_id': user.id}))
    assert resp.status_code == 200

def test_vacancies_get(client):
    """Тест GET-запроса к представлению списка вакансий."""
    resp = client.get(reverse('vacancies_list'))
    assert resp.status_code == 200

@patch('RecruitHelper.views.ChatGPT.get_response')
def test_add_vacancy_post(mock_gpt, client, company):
    """Тест POST-запроса к представлению добавления вакансии."""
    client.force_login(company)
    mock_gpt.return_value = {'rating': 5, 'tags': []}
    resp = client.post(reverse('add_vacancy'), {
        'title': 'Test', 'geography': 'City', 'description': 'Desc'
    })
    assert resp.status_code in (302, 200)

def test_vacancy_detail(client, user):
    """Тест представления детальной страницы вакансии."""
    vac = Vacancy.objects.create(title='T', description='D', geography={}, ai_rating=1)
    client.force_login(user)
    resp = client.get(reverse('vacancy', kwargs={'vacancy_id': vac.id}))
    assert resp.status_code == 200

@patch('RecruitHelper.views.ChatGPT.get_response')
def test_apply_to_vacancy(mock_gpt, client, user, company):
    """Тест представления подачи заявки на вакансию."""
    vac = Vacancy.objects.create(title='T',
                                 description='D',
                                 geography={},
                                 ai_rating=1,
                                 company=company.company)
    client.force_login(user)
    mock_gpt.return_value = '{"rating": 1}'
    resp = client.get(reverse('apply_to_vacancy', kwargs={'vacancy_id': vac.id}))
    assert resp.status_code in (302, 200)

def test_privacy_news_about(client):
    """Тест представлений для статических страниц (privacy, news, about)."""
    assert client.get(reverse('privacy')).status_code == 200
    assert client.get(reverse('news')).status_code == 200
    assert client.get(reverse('about_us')).status_code == 200

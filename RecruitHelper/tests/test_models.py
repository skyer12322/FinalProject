"""Тесты для Django Models."""

import pytest
from RecruitHelper.models import User, CUser, Company, Vacancy, Application, Chat, Message
from RecruitHelper.models import CustomUserManager, Notification

pytestmark = pytest.mark.django_db

def test_user_manager_and_str():
    """Тест менеджера пользователей и строкового представления пользователя."""
    user = User.objects.create_user(email='a@a.com', password='pass', main_name='A')
    assert user.email == 'a@a.com'
    assert str(user) == 'a@a.com'
    assert user.check_password('pass')

def test_create_user_no_email():
    """Тест создания пользователя без email."""
    with pytest.raises(ValueError):
        CustomUserManager().create_user(email=None, password='pass')

def test_cuser_and_company_str():
    """Тест строкового представления обычного пользователя и компании."""
    user = User.objects.create_user(email='b@b.com', password='pass', main_name='B')
    cuser = CUser.objects.create(user=user, first_name='F', last_name='L')
    assert str(cuser) == 'F L'
    company = Company.objects.create(user=user)
    assert str(company) == user.main_name

def test_vacancy_and_application_str():
    """Тест строкового представления вакансии и заявки."""
    user = User.objects.create_user(email='c@c.com', password='pass', main_name='C', role='company')
    company = Company.objects.create(user=user)
    vacancy = Vacancy.objects.create(
        title='V', description='D', geography={'city': 'Test'}, ai_rating=5, company=company
    )
    assert str(vacancy) == 'V'
    cuser = CUser.objects.create(user=User.objects.create_user(email='d@d.com',
                                                               password='pass',
                                                               main_name='D'))
    app = Application.objects.create(vacancy=vacancy, candidate=cuser)
    assert 'подал заявку' in str(app)

def test_chat_and_message_str():
    """Тест строкового представления чата и сообщения."""
    user1 = User.objects.create_user(email='c@c.com',
                                     password='pass',
                                     main_name='C',
                                     role='company')
    company = Company.objects.create(user=user1)
    user2 = User.objects.create_user(email='d@d.com', password='pass', main_name='D')
    cuser = CUser.objects.create(user=user2)
    vacancy = Vacancy.objects.create(
        title='V', description='D', geography={'city': 'Test'}, ai_rating=5, company=company
    )
    chat = Chat.objects.create(user=cuser, company=company, vacancy=vacancy, name='chat')
    msg1 = Message.objects.create(user=user1, content='msg')
    msg2 = Message.objects.create(user=user2, content='msg2')
    chat.messages.add(msg1, msg2)
    assert str(msg1.user) in str(msg1)
    assert str(msg2.user) in str(msg2)
    assert f'Chat {chat.id}' in str(chat)

def test_notification_str():
    """Тест строкового представления уведомления."""
    user = User.objects.create_user(email='e@e.com', password='pass', main_name='E')
    company = Company.objects.create(user=user)
    vacancy = Vacancy.objects.create(
        title='V2', description='D2', geography={'city': 'Test'}, ai_rating=4, company=company
    )
    chat = Chat.objects.create(vacancy=vacancy)
    notif = Notification.objects.create(
        user=user, notification_type='application', title='T', vacancy=vacancy, chat=chat
    )
    assert 'Заявка' in str(notif)

import pytest
from RecruitHelper.models import User, CUser, Company, Vacancy, Application, Chat, ChatMessage, Notification
from django.utils import timezone

pytestmark = pytest.mark.django_db

def test_user_manager_and_str():
    user = User.objects.create_user(email='a@a.com', password='pass', main_name='A')
    assert user.email == 'a@a.com'
    assert str(user) == 'a@a.com'
    assert user.check_password('pass')

def test_create_user_no_email():
    from RecruitHelper.models import CustomUserManager
    with pytest.raises(ValueError):
        CustomUserManager().create_user(email=None, password='pass')

def test_cuser_and_company_str():
    user = User.objects.create_user(email='b@b.com', password='pass', main_name='B')
    cuser = CUser.objects.create(user=user, first_name='F', last_name='L')
    assert str(cuser) == 'F L'
    company = Company.objects.create(user=user)
    assert str(company) == user.main_name

def test_vacancy_and_application_str():
    user = User.objects.create_user(email='c@c.com', password='pass', main_name='C', role='company')
    company = Company.objects.create(user=user)
    chat = Chat.objects.create()
    vacancy = Vacancy.objects.create(
        title='V', description='D', geography={'city': 'Test'}, ai_rating=5, company=company, chats=chat
    )
    assert str(vacancy) == 'V'
    cuser = CUser.objects.create(user=User.objects.create_user(email='d@d.com', password='pass', main_name='D'))
    app = Application.objects.create(vacancy=vacancy, candidate=cuser)
    assert 'подал заявку' in str(app)

def test_chat_and_message_str():
    chat = Chat.objects.create()
    msg1 = ChatMessage.objects.create(user=1, company=-1, content='msg')
    msg2 = ChatMessage.objects.create(user=-1, company=2, content='msg2')
    chat.messages.add(msg1, msg2)
    assert 'User' in str(msg1)
    assert 'Company' in str(msg2)
    assert f'Chat {chat.id}' == str(chat)

def test_notification_str():
    user = User.objects.create_user(email='e@e.com', password='pass', main_name='E')
    vacancy = Vacancy.objects.create(
        title='V2', description='D2', geography={'city': 'Test'}, ai_rating=4
    )
    chat = Chat.objects.create()
    notif = Notification.objects.create(
        user=user, notification_type='application', title='T', vacancy=vacancy, chat=chat
    )
    assert 'Заявка' in str(notif)

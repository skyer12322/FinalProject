"""
Модуль с тестами для WebSocket.
"""
import pytest
from django.urls import path
from channels.testing import WebsocketCommunicator
from channels.routing import URLRouter
from RecruitHelper.models import Chat, CUser, Company, Vacancy
from FinalProject.consumers import ChatConsumer

pytestmark = pytest.mark.django_db(transaction=True)

@pytest.fixture
def user(django_user_model):
    """
    Фикстура пользователя
    """
    user = django_user_model.objects.create_user(
        email='user@test.com', password='pass', main_name='User'
    )
    cuser = CUser.objects.create(user=user, first_name='Test', last_name='User')
    return cuser

@pytest.fixture
def company(django_user_model):
    """
    Фикстура компании
    """
    user = django_user_model.objects.create_user(
        email='company@test.com', password='pass', main_name='Company', role='company'
    )
    company = Company.objects.create(user=user)
    return company

@pytest.fixture
def chat(user, company):
    """
    Фикстура чата
    """
    vacancy = Vacancy.objects.create(title='Test Vacancy',
                                    description='Test Description',
                                    company=company,
                                    geography={},
                                    ai_rating=1)
    chat = Chat.objects.create(vacancy=vacancy, user=user, company=company)
    chat.save()
    return chat

@pytest.mark.asyncio
async def test_connect_user_access(user, chat):
    """
    Тест подключения пользователя и получения доступа
    """
    application = URLRouter([path("ws/chat/<int:chat_id>/", ChatConsumer.as_asgi())])
    communicator = WebsocketCommunicator(application, f"/ws/chat/{chat.id}/")
    communicator.scope['user'] = user.user
    communicator.scope['url_route'] = {'kwargs': {'chat_id': chat.id}}
    connected, _ = await communicator.connect(timeout=5)
    assert connected
    await communicator.disconnect()

@pytest.mark.asyncio
async def test_connect_no_access(user):
    """
    Тест подключения пользователя и запрета доступа
    """
    application = URLRouter([path("ws/chat/<int:chat_id>/", ChatConsumer.as_asgi())])
    communicator = WebsocketCommunicator(application, "/ws/chat/9999/")
    communicator.scope['user'] = user.user
    communicator.scope['url_route'] = {'kwargs': {'chat_id': 9999}}
    connected, _ = await communicator.connect(timeout=5)
    assert not connected
    await communicator.disconnect()

@pytest.mark.asyncio
async def test_send_and_receive_message(user, chat):
    """
    Тест отправки и получения сообщения
    """
    application = URLRouter([path("ws/chat/<int:chat_id>/", ChatConsumer.as_asgi())])
    communicator = WebsocketCommunicator(application, f"/ws/chat/{chat.id}/")
    communicator.scope['user'] = user.user
    communicator.scope['url_route'] = {'kwargs': {'chat_id': chat.id}}
    connected, _ = await communicator.connect()
    assert connected
    msg = {"content": "hello!"}
    await communicator.send_json_to(msg)
    response = await communicator.receive_json_from()
    assert response["content"] == "hello!"
    assert response["user"]["main_name"] == user.user.main_name
    await communicator.disconnect()

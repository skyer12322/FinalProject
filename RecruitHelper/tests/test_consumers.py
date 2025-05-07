import pytest
import json
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from RecruitHelper.models import Chat, CUser, Company, Message, Vacancy
from FinalProject.consumers import ChatConsumer

pytestmark = pytest.mark.django_db(transaction=True)

@pytest.fixture
def user(django_user_model):
    user = django_user_model.objects.create_user(
        email='user@test.com', password='pass', main_name='User'
    )
    cuser = CUser.objects.create(user=user, first_name='Test', last_name='User')
    return user

@pytest.fixture
def company(django_user_model):
    user = django_user_model.objects.create_user(
        email='company@test.com', password='pass', main_name='Company', role='company'
    )
    company = Company.objects.create(user=user)
    return user

@pytest.fixture
def chat(user, company):
    from RecruitHelper.models import Vacancy
    vacancy = Vacancy.objects.create(title='Test Vacancy', description='Test Description', company=company.company, geography={}, ai_rating=1)
    chat = Chat.objects.create(vacancy=vacancy, user=user.cuser, company=company.company)
    chat.save()
    return chat

@pytest.mark.asyncio
async def test_connect_user_access(user, chat):
    from channels.routing import URLRouter
    from django.urls import path
    application = URLRouter([path("ws/chat/<int:chat_id>/", ChatConsumer.as_asgi())])
    communicator = WebsocketCommunicator(application, f"/ws/chat/{chat.id}/")
    communicator.scope['user'] = user
    communicator.scope['url_route'] = {'kwargs': {'chat_id': chat.id}}
    connected, _ = await communicator.connect(timeout=5)
    assert connected
    await communicator.disconnect()

@pytest.mark.asyncio
async def test_connect_no_access(user):
    from channels.routing import URLRouter
    from django.urls import path
    application = URLRouter([path("ws/chat/<int:chat_id>/", ChatConsumer.as_asgi())])
    communicator = WebsocketCommunicator(application, f"/ws/chat/9999/")
    communicator.scope['user'] = user
    communicator.scope['url_route'] = {'kwargs': {'chat_id': 9999}}
    connected, _ = await communicator.connect(timeout=5)
    assert not connected
    await communicator.disconnect()

@pytest.mark.asyncio
async def test_send_and_receive_message(user, chat):
    from channels.routing import URLRouter
    from django.urls import path
    application = URLRouter([path("ws/chat/<int:chat_id>/", ChatConsumer.as_asgi())])
    communicator = WebsocketCommunicator(application, f"/ws/chat/{chat.id}/")
    communicator.scope['user'] = user
    communicator.scope['url_route'] = {'kwargs': {'chat_id': chat.id}}
    connected, _ = await communicator.connect()
    assert connected
    msg = {"content": "hello!"}
    await communicator.send_json_to(msg)
    response = await communicator.receive_json_from()
    assert response["content"] == "hello!"
    assert response["user"]["main_name"] == user.main_name
    await communicator.disconnect()

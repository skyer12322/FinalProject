from django.test import TestCase
from RecruitHelper.models import ChatMessage, Chat, Vacancy, CUser, Pendings, Company
import json

class ModelTests(TestCase):
    def setUp(self):
        self.user = CUser.objects.create_user(
            email='user@example.com',
            username='testuser',
            first_name='John',
            last_name='Doe',
            password='testpass123',
            phone='1234567890'
        )
        self.company = Company.objects.create_user(
            email='company@example.com',
            company_name='Test Company',
            password='testpass123',
            phone='0987654321'
        )
        self.vacancy = Vacancy.objects.create(
            title='Software Engineer',
            description='Backend Developer',
            ai_rating=5,
            company=self.company
        )
        self.chat_message = ChatMessage.objects.create(
            user=self.user,
            company=self.company,
            content='Hello, World!'
        )
        self.pending = Pendings.objects.create(
            vacancy=self.vacancy,
            candidate=self.user,
            ai_rating=4
        )

    def test_cuser_model(self):
        self.assertEqual(self.user.email, 'user@example.com')
        self.assertEqual(str(self.user), 'John Doe')
        self.assertTrue(self.user.check_password('testpass123'))

    def test_company_model(self):
        self.assertEqual(self.company.company_name, 'Test Company')
        self.assertEqual(str(self.company), 'Test Company')

    def test_vacancy_model(self):
        self.assertEqual(self.vacancy.title, 'Software Engineer')
        self.assertEqual(str(self.vacancy), 'Software Engineer')
        self.assertEqual(self.vacancy.ai_rating, 5)  # Проверка ai_rating

    def test_chat_message_model(self):
        self.assertEqual(self.chat_message.content, 'Hello, World!')
        self.assertEqual(self.chat_message.user, self.user)
        self.assertEqual(self.chat_message.company, self.company)

    def test_pendings_model(self):
        self.assertEqual(str(self.pending), 'John Doe подал заявку на вакансию Software Engineer')
        self.assertEqual(self.pending.ai_rating, 4)

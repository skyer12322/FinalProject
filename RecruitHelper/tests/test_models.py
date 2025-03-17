from django.test import TestCase
from django.contrib.auth import get_user_model
from RecruitHelper.models import ChatMessage, Chat, Vacancy, CUser, Pendings, Company
from django.core.files.uploadedfile import SimpleUploadedFile
import json

class ModelTests(TestCase):
    def setUp(self):
        self.user = CUser.objects.create_user(
            email='user@example.com',
            username='testuser',
            first_name='John',
            last_name='Doe',
            password='testpass123'
        )
        self.company = Company.objects.create_user(
            email='company@example.com',
            company_name='Test Company',
            password='testpass123'
        )
        self.vacancy = Vacancy.objects.create(
            title='Software Engineer',
            description='Backend Developer',
            required_skills=json.dumps(['Python', 'Django']),
            required_experience=2,
            required_education='Bachelor',
            ai_rating=5,
            company=self.company
        )
        self.chat_message = ChatMessage.objects.create(
            user=self.user.id,
            company=self.company.id,
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

    def test_company_model(self):
        self.assertEqual(self.company.company_name, 'Test Company')
        self.assertEqual(str(self.company), 'Test Company')

    def test_vacancy_model(self):
        self.assertEqual(self.vacancy.title, 'Software Engineer')
        self.assertEqual(str(self.vacancy), 'Software Engineer')

    def test_pendings_model(self):
        self.assertEqual(str(self.pending), 'John Doe подал заявку на вакансию Software Engineer')
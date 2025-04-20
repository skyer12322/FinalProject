from django.test import TestCase
from RecruitHelper.forms import VacancyForm, VacancyFilterForm
from RecruitHelper.models import Vacancy
import json

class VacancyFilterFormTest(TestCase):
    def test_vacancy_filter_form_valid(self):
        form_data = {
            'category': 'IT',
            'city': 'New York',
            'min_salary': 50000,
            'max_salary': 100000
        }
        form = VacancyFilterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_vacancy_filter_form_empty(self):
        form_data = {}
        form = VacancyFilterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_vacancy_filter_form_invalid_salary(self):
        form_data = {
            'min_salary': 100000,
            'max_salary': 50000
        }
        form = VacancyFilterForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('non_field_errors', form.errors)


class VacancyFormTest(TestCase):
    def test_vacancy_form_valid(self):
        form_data = {
            'title': 'Software Engineer',
            'description': 'Backend Developer',
            'geography': json.dumps({'country': 'USA', 'city': 'New York'}),
            'ai_rating': 5,
            'tags_ai': json.dumps(['Python', 'Django']),
            # Предполагаем, что поле chats не обязательно для создания вакансии
            # Если у вас есть связанные чаты, добавьте их здесь
        }
        form = VacancyForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_vacancy_form_invalid_ai_rating(self):
        form_data = {
            'title': 'Software Engineer',
            'description': 'Backend Developer',
            'geography': json.dumps({'country': 'USA', 'city': 'New York'}),
            'ai_rating': -1,  # Неверное значение для ai_rating
            'tags_ai': json.dumps(['Python', 'Django']),
        }
        form = VacancyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('ai_rating', form.errors)  # Проверяем ошибку здесь

    def test_vacancy_form_invalid_tags_ai(self):
        form_data = {
            'title': 'Software Engineer',
            'description': 'Backend Developer',
            'geography': json.dumps({'country': 'USA', 'city': 'New York'}),
            'ai_rating': 5,
            'tags_ai': "not a json",  # Некорректный JSON
        }
        form = VacancyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('tags_ai', form.errors)  # Проверяем ошибку здесь

    def test_vacancy_form_missing_required_fields(self):
        form_data = {
            # Отсутствуют обязательные поля title и description
            'geography': json.dumps({'country': 'USA', 'city': 'New York'}),
            'ai_rating': 5,
            'tags_ai': json.dumps(['Python', 'Django']),
        }
        form = VacancyForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)  # Проверяем ошибку для title
        self.assertIn('description', form.errors)  # Проверяем ошибку для description

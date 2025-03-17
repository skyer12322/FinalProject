from django.test import TestCase
from RecruitHelper.forms import VacancyForm, VacancyFilterForm
from RecruitHelper.models import Vacancy
import json

class VacancyFormTest(TestCase):
    def test_vacancy_form_valid(self):
        # Корректные данные
        form_data = {
            'title': 'Software Engineer',
            'description': 'Backend Developer',
            'required_skills': json.dumps(['Python', 'Django']),
            'required_experience': '2',  # Число в виде строки
            'required_education': 'Bachelor'
        }
        form = VacancyForm(data=form_data)
        self.assertTrue(form.is_valid())  # Форма должна быть валидной

    def test_vacancy_form_invalid(self):
        # Некорректные данные (required_experience не число)
        form_data = {
            'title': 'Software Engineer',
            'description': 'Backend Developer',
            'required_skills': json.dumps(['Python', 'Django']),
            'required_experience': 'two',  # Не число
            'required_education': 'Bachelor'
        }
        form = VacancyForm(data=form_data)
        self.assertFalse(form.is_valid())  # Форма должна быть невалидной
        self.assertIn('required_experience', form.errors)  # Ошибка должна быть в поле required_experience

    def test_clean_required_experience(self):
        # Проверка метода clean_required_experience
        form_data = {
            'title': 'Software Engineer',
            'description': 'Backend Developer',
            'required_skills': json.dumps(['Python', 'Django']),
            'required_experience': '2',  # Число в виде строки
            'required_education': 'Bachelor'
        }
        form = VacancyForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['required_experience'], 2)  # Значение должно быть преобразовано в int

class VacancyFilterFormTest(TestCase):
    def test_vacancy_filter_form_valid(self):
        # Корректные данные
        form_data = {
            'category': 'IT',
            'city': 'New York',
            'min_salary': 50000,
            'max_salary': 100000
        }
        form = VacancyFilterForm(data=form_data)
        self.assertTrue(form.is_valid())  # Форма должна быть валидной

    def test_vacancy_filter_form_empty(self):
        # Пустые данные (все поля не обязательны)
        form_data = {}
        form = VacancyFilterForm(data=form_data)
        self.assertTrue(form.is_valid())  # Форма должна быть валидной

    def test_vacancy_filter_form_invalid_salary(self):
        # Некорректные данные (min_salary > max_salary)
        form_data = {
            'min_salary': 100000,
            'max_salary': 50000
        }
        form = VacancyFilterForm(data=form_data)
        self.assertTrue(form.is_valid())  # Форма должна быть валидной, так как валидация на min < max не реализована
        # Если вы добавите такую валидацию, замените на self.assertFalse(form.is_valid())
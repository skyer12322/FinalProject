"""Тесты для Django Forms."""

import pytest
from RecruitHelper.forms import (
    UserRegistrationForm, VacancyForm, EditUserForm, EditCUserForm, EditCompanyForm,
    VacancyFilterForm
)
from RecruitHelper.models import User, Company, CUser

pytestmark = pytest.mark.django_db

def test_user_registration_form_valid_invalid():
    """Тест валидности формы регистрации пользователя."""
    form = UserRegistrationForm(data={'main_name': 'X', 'email': 'x@x.com', 'password': '123'})
    assert form.is_valid()
    form = UserRegistrationForm(data={'main_name': '', 'email': '', 'password': ''})
    assert not form.is_valid()

def test_vacancy_form_required():
    """Тест обязательных полей формы вакансии."""
    form = VacancyForm(data={'title': '', 'geography': '', 'description': '', 'currency': ''})
    assert not form.is_valid()
    form = VacancyForm(data={'title': 'T', 'geography': 'G', 'description': 'D', 'currency': 'RUB'})
    assert form.is_valid()

def test_edit_user_form_and_company():
    """Тест форм редактирования пользователя и компании."""
    user = User.objects.create_user(email='a@a.com',
                                    password='pass',
                                    main_name='A',
                                    description='desc')
    form = EditUserForm(data={
        'main_name': 'B', 'email': 'b@b.com', 'description': 'desc'
    }, instance=user)
    assert form.is_valid()
    company = Company.objects.create(user=user)
    form2 = EditCompanyForm(data={'website': 'mysite.com'}, instance=company)
    assert form2.is_valid()

def test_edit_cuser_form():
    """Тест формы редактирования обычного пользователя (CUser)."""
    user = User.objects.create_user(email='c@c.com', password='pass', main_name='C')
    cuser = CUser.objects.create(user=user, first_name='F', last_name='L')
    form = EditCUserForm(data={'first_name': 'F2', 'last_name': 'L2'}, instance=cuser)
    assert form.is_valid()

def test_vacancy_filter_form_variants():
    """Тест формы фильтрации вакансий с различными вариантами ввода."""
    form = VacancyFilterForm(data={'category': 'it',
                                   'city': 'Moscow', 
                                   'min_salary': 1000, 
                                   'max_salary': 2000})
    assert form.is_valid()
    form = VacancyFilterForm(data={'min_salary': 'wrong'})
    assert not form.is_valid()

from django import forms

from .models import Vacancy

class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = (
            'title',
            'description',
            'required_skills',
            'required_experience',
            'required_education',
        )

class VacancyFilterForm(forms.Form):
    category = forms.CharField(required=False, label="Категория")
    city = forms.CharField(required=False, label="Город")
    min_salary = forms.DecimalField(required=False, label="Минимальная зарплата")
    max_salary = forms.DecimalField(required=False, label="Максимальная зарплата")
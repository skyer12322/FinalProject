from django import forms
from tinymce.widgets import TinyMCE
from .models import Vacancy, CUser

class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = (
            'title',
            'description',
        )

class VacancyFilterForm(forms.Form):
    category = forms.CharField(required=False, label="Категория")
    city = forms.CharField(required=False, label="Город")
    min_salary = forms.DecimalField(required=False, label="Минимальная зарплата")
    max_salary = forms.DecimalField(required=False, label="Максимальная зарплата")
class ProfileForm(forms.ModelForm):
    biography = forms.CharField(widget=TinyMCE(attrs={'cols': 80, 'rows': 20}))

    class Meta:
        model = CUser
        fields = ['biography']

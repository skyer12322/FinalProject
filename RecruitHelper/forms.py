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
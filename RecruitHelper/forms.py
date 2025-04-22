from django import forms
from .models import Vacancy, User

class VacancyForm(forms.ModelForm):
    title = forms.CharField(required=True, label="Название вакансии" , widget=forms.TextInput(attrs={'placeholder': 'Название вакансии',
                                                                                                     'class': 'form-control container',}))
    geography = forms.CharField(required=True, label="Город" , widget=forms.TextInput(attrs={'placeholder': 'Город',
                                                                                             'class': 'form-control container',}))
    description = forms.CharField(required=True, label="Описание вакансии" , widget=forms.Textarea(attrs={'placeholder': 'Описание вакансии',
                                                                                                          'class': 'form-control container',}))
    tags_ai = forms.CharField(required=False, label="Теги" , widget=forms.TextInput(attrs={'placeholder': 'Теги (через пробел)',
                                                                                           'class': 'form-control container',}))

    class Meta:
        model = Vacancy
        fields = (
            'title',
            'geography',
            'description',
            'tags_ai',
        )
        
class UserRegistrationForm(forms.ModelForm):
    main_name = forms.CharField(
        required=True,
        label="Имя пользователя / компании",
        widget=forms.TextInput(attrs={
            'placeholder': 'Имя пользователя / компании',
            'class': 'form-control',
            'autocomplete': 'off'
        })
    )
    email = forms.EmailField(
        required=True,
        label="Email",
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email',
            'class': 'form-control',
            'autocomplete': 'off'
        })
    )
    password = forms.CharField(
        required=True,
        label="Пароль",
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Пароль',
            'class': 'form-control',
            'autocomplete': 'new-password'
        })
    )
    class Meta:
        model = User
        fields = ('main_name', 'email', 'password')

class VacancyFilterForm(forms.Form):
    category = forms.CharField(required=False, label="Категория")
    city = forms.CharField(required=False, label="Город")
    min_salary = forms.DecimalField(required=False, label="Минимальная зарплата")
    max_salary = forms.DecimalField(required=False, label="Максимальная зарплата")
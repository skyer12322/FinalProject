"""
Модуль с формами для приложения RecruitHelper.
"""
from django import forms
from .models import Vacancy, User, Company, CUser

class VacancyForm(forms.ModelForm):
    """
    Форма для создания и редактирования вакансий.
    """
    title = forms.CharField(required=True, label="Название вакансии",
                            widget=forms.TextInput(attrs={'placeholder': 'Название вакансии',
                                                          'class': 'form-control container',}))
    geography = forms.CharField(required=True,
                                label="Город",
                                widget=forms.TextInput(attrs={'placeholder': 'Город',
                                                              'class': 'form-control container',}))
    description = forms.CharField(required=True,
                                  label="Описание вакансии" ,
                                  widget=forms.Textarea(attrs={'placeholder': 'Описание вакансии',
                                                               'class': 'form-control container',}))
    tags_ai = forms.CharField(required=False,
                              label="Теги",
                              widget=forms.TextInput(attrs={'placeholder': 'Теги (через пробел)',
                                                            'class': 'form-control container',}))

    class Meta:
        """
        Мета-опции формы VacancyForm.
        """
        model = Vacancy
        fields = (
            'title',
            'geography',
            'description',
            'tags_ai',
        )

class UserRegistrationForm(forms.ModelForm):
    """
    Форма для регистрации новых пользователей (соискателей или компаний).
    """
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
        """
        Мета-опции формы UserRegistrationForm.
        """
        model = User
        fields = ('main_name', 'email', 'password')

class EditUserForm(forms.ModelForm):
    """
    Базовая форма для редактирования профиля пользователя.
    """
    profile_image = forms.FileField(
        required=False,
        label="Аватар",
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        })
    )
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
    description = forms.CharField(
        required=True,
        label="Описание",
        widget=forms.Textarea(attrs={
            'placeholder': 'Описание',
            'class': 'form-control',
            'rows': 5
        })
    )

    class Meta:
        """
        Мета-опции формы EditUserForm.
        """
        model = User
        fields = ('main_name', 'email', 'description', 'profile_image')

class EditCUserForm(forms.ModelForm):
    """
    Форма для редактирования профиля рядового пользователя.
    """
    first_name = forms.CharField(
        required=True,
        label="Имя",
        widget=forms.TextInput(attrs={
            'placeholder': 'Имя',
            'class': 'form-control',
            'autocomplete': 'off'
        })
    )
    last_name = forms.CharField(
        required=True,
        label="Фамилия",
        widget=forms.TextInput(attrs={
            'placeholder': 'Фамилия',
            'class': 'form-control',
            'autocomplete': 'off'
        })
    )
    resume = forms.FileField(
        required=False,
        label="Резюме",
        widget=forms.FileInput(attrs={
            'class': 'form-control'
        })
    )
    class Meta:
        """
        Мета-опции формы EditCUserForm.
        """
        model = CUser
        fields = ('first_name', 'last_name', 'resume')

class EditCompanyForm(forms.ModelForm):
    """
    Форма для редактирования профиля компании.
    """
    website = forms.CharField(
        required=False,
        label="Сайт",
        widget=forms.TextInput(attrs={'placeholder': 'Сайт', 'class': 'form-control'})
    )
    class Meta:
        """
        Мета-опции формы EditCompanyForm.
        """
        model = Company
        fields = ('website',)

class VacancyFilterForm(forms.Form):
    """
    Форма для фильтрации вакансий.
    """
    category = forms.CharField(required=False, label="Категория")
    city = forms.CharField(required=False, label="Город")
    min_salary = forms.DecimalField(required=False, label="Минимальная зарплата")
    max_salary = forms.DecimalField(required=False, label="Максимальная зарплата")

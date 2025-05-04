from django import forms
from .models import Vacancy, User, Company, CUser

class VacancyForm(forms.ModelForm):
    title = forms.CharField(required=True, label="Название вакансии" , widget=forms.TextInput(attrs={'placeholder': 'Название вакансии',
                                                                                                     'class': 'form-control container',}))
    geography = forms.CharField(required=True, label="Город" , widget=forms.TextInput(attrs={'placeholder': 'Город',
                                                                                             'class': 'form-control container',}))
    description = forms.CharField(required=True, label="Описание вакансии" , widget=forms.Textarea(attrs={'placeholder': 'Описание вакансии',
                                                                                                          'class': 'form-control container',}))

    class Meta:
        model = Vacancy
        fields = (
            'title',
            'geography',
            'description',
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

class EditUserForm(forms.ModelForm):
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
        model = User
        fields = ('main_name', 'email', 'description', 'profile_image')
        
class EditCUserForm(forms.ModelForm):
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
        model = CUser
        fields = ('first_name', 'last_name', 'resume')

class EditCompanyForm(forms.ModelForm):
    website = forms.CharField(
        required=False,
        label="Сайт",
        widget=forms.TextInput(attrs={'placeholder': 'Сайт', 'class': 'form-control'})
    )
    class Meta:
        model = Company
        fields = ('website',)

class VacancyFilterForm(forms.Form):
    category = forms.CharField(required=False, label="Категория")
    city = forms.CharField(required=False, label="Город")
    min_salary = forms.DecimalField(required=False, label="Минимальная зарплата")
    max_salary = forms.DecimalField(required=False, label="Максимальная зарплата")
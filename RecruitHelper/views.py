from django.shortcuts import render, redirect, get_object_or_404
from .models import *
from .forms import *
from django import forms
import random

def home(req):
    vacancies_context = list()
    vacancy_count = Vacancy.objects.count()
    if vacancy_count > 4:
        vacancy_ids = list(Vacancy.objects.values_list('id', flat=True))
        random_ids = random.sample(vacancy_ids, 4)
        for vacancy_id in random_ids:
            vacancy = Vacancy.objects.get(id=vacancy_id)
            vacancies_context.append(vacancy)
    else:
        vacancies_context = Vacancy.objects.all()
    context = {"vacancies": vacancies_context}
    return render(req, 'main/index.html', context)

def login(req):
    context = { }
    return render(req, 'auth/login.html', context)

def register(req):
    context = { }
    return render(req, 'auth/registration.html', context)

def company(req):
    context = { }
    return render(req, 'users/HRpage.html', context)

def login(req):
    context = { }
    return render(req, 'auth/login.html', context)

def profile(req):
    context = { }
    return render(req, 'users/profile.html',context)

def candidate(req):
    context = { }
    return render(req, 'users/candidatepage.html',context)

class VacancyForm(forms.ModelForm):
    class Meta:
        model = Vacancy
        fields = ['title', 'description', 'required_skills', 'required_experience', 'required_education']
        widgets = {
            'required_skills': forms.Textarea(attrs={'placeholder': 'Skills (comma-separated)'}),
        }


def vacancies(request):
    vacancies = Vacancy.objects.all()  # Получаем все вакансии
    form = VacancyFilterForm(request.GET or None)

    if form.is_valid():
        category = form.cleaned_data.get('category')
        city = form.cleaned_data.get('city')
        min_salary = form.cleaned_data.get('min_salary')
        max_salary = form.cleaned_data.get('max_salary')

        # Фильтрация
        if category:
            vacancies = vacancies.filter(category__icontains=category)
        if city:
            vacancies = vacancies.filter(city__icontains=city)
        if min_salary:
            vacancies = vacancies.filter(salary__gte=min_salary)
        if max_salary:
            vacancies = vacancies.filter(salary__lte=max_salary)
    return render(request, 'vacancies/vacancy_list.html', {'form': form, 'vacancies': vacancies})


def add_vacancy(request):
    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('vacancies_list')
    else:
        form = VacancyForm()

    return render(request, 'vacancies/add_vacancy.html', {'form': form})

def vacancy(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    return render(request, 'vacancies/vacancy_detail.html', {'vacancy': vacancy})

def news(request):
    return render(request, 'vacancies/news.html')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .models import *
from .forms import *
from django.core.exceptions import ValidationError
from .decorators import anonymous_required, company_required, user_required
from django.contrib.auth.decorators import login_required
import random
from .ChatGPT_API import ChatGPT
from . import prompts
import os
from openai import OpenAI
import json



def home(request):
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
    return render(request, 'main/index.html', context)

@anonymous_required
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")
        is_company = request.POST.get("CompanyLoginCheckbox") == "on"

        backend = 'RecruitHelper.backends.CompanyAuthBackend' if is_company else 'RecruitHelper.backends.CUserAuthBackend'

        if is_company:
            user = authenticate(request, company_email=email, password=password)
        else:
            user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return render(request, "auth/login.html", {"error": "Неверный email или пароль"})

    return render(request, "auth/login.html")

@anonymous_required
def register(request):
    if request.method == 'POST':
        is_company = 'CompanyRegistrationCheckbox' in request.POST
        try:
            if is_company:
                company_name = request.POST.get('company_name')
                company_email = request.POST.get('company_email')
                company_phone = request.POST.get("company_phone_prefix") + ' ' + request.POST.get('company_phone')
                password = request.POST.get('company_password')

                if Company.objects.filter(email=company_email).exists():
                    raise ValidationError('Компания с таким email уже зарегистрирована')

                Company.objects.create_user(
                    company_name=company_name,
                    email=company_email,
                    phone=company_phone,
                    password=password
                )
            else:
                username = request.POST.get('username')
                email = request.POST.get('email')
                password = request.POST.get('password')

                if CUser.objects.filter(email=email).exists():
                    raise ValidationError('Пользователь с таким email уже существует')

                CUser.objects.create_user(
                    first_name=request.POST.get('first_name'),
                    last_name=request.POST.get('last_name'),
                    username=username,
                    email=email,
                    phone=request.POST.get("phone_prefix") + request.POST.get('phone'),
                    password=password
                )
            return redirect('/')
        except ValidationError as e:
            return render(request, 'auth/registration.html', {'error': e.messages})
    return render(request, 'auth/registration.html')

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

def company(req, company_id):
    context = {"company_object": Company.objects.filter(id=company_id)}
    return render(req, 'users/HRpage.html', context)

@login_required
def profile(req):
    user = req.user 
    context = {
        'user': user,
    }
    return render(req, 'users/profile.html',context)

def candidate(req, user_id):
    candidate_user = get_object_or_404(CUser, id=user_id)
    context = {
        'candidate': candidate_user
    }
    return render(req, 'users/candidatepage.html',context)

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

def user_pendings(request):
    context = {}
    return render(request, 'user_pendings.html', context)

@login_required
@company_required
def add_vacancy(request):
    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            vacancy = Vacancy(
                    title=form.cleaned_data['title'],
                    description=form.cleaned_data['description'],
                    geography=form.cleaned_data['geography'],
                    company=request.user
                )
            try:
                api_key = os.getenv("OPENAI_API_KEY")
                client = ChatGPT(
                    api_key=api_key,
                )
                response_text = client.get_response(prompts.JOB_RANKING, vacancy.description)
                vacancy.ai_rating = int(response_text['rating'])
                tags_text = client.get_response(prompts.TAGS_ASSIGN, f'{vacancy.title}\n{vacancy.description}')
                if form.cleaned_data['tags_ai']:
                    for elem in form.cleaned_data['tags_ai'].split():
                        tags_text['tags'].append(elem)
                vacancy.tags_ai = tags_text
                    
            except Exception as e:
                print(f"AI бунтует! Произошла ошибка {e}.")
                vacancy.ai_rating = 0
                
            vacancy.save()
            request.user.vacancies.add(vacancy)
            request.user.save()
            return redirect('vacancies_list')
    else:
        form = VacancyForm()
    return render(request, 'vacancies/add_vacancy.html', {'form': form})

@login_required
def vacancy(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    return render(request, 'vacancies/vacancy_detail.html', {'vacancy': vacancy})

@login_required
@user_required
def apply_to_vacancy(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    pending = Pendings.objects.create(
        vacancy=vacancy,
        candidate=request.user
    )
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        client = ChatGPT(
            api_key=api_key,
        )
        content = f"Вакансия: {vacancy.description}\n\nРезюме кандидата: {request.user.resume}"
        response_text = client.get_response(prompts.JOB_RANKING_CANDIDATE, content)
        print(response_text)
        response_data = json.loads(response_text)
        pending.ai_rating = int(response_data['rating'])
                    
    except Exception as e:
        print(f"AI бунтует! Произошла ошибка {e}.")
        pending.ai_rating = 0
    pending.save()
    return redirect('profile')

def privacy(request):
    return render(request, 'info/privacy_policy.html')

def news(request):
    return render(request, 'vacancies/news.html')

def about_us(req):
    context = { }
    return render(req, 'info/about_us.html', context)


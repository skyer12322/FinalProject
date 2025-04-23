from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .models import *
from .forms import *
from django.core.exceptions import ValidationError
from .decorators import anonymous_required
from django.contrib.auth.decorators import login_required
import random
from .chatgpt import ChatGPT
from . import prompts
import os
import json
from collections import defaultdict, Counter


def bel():
    for elem in CUser.objects.all():
        print(elem, elem['id'])
    return


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
    
    tags = set()
    for vacancy in Vacancy.objects.all():
        try:
            ai_tags = vacancy.tags_ai.get("tags", {})
        except Exception:
            continue
        for _, tags_list in ai_tags.items():
            for tag in tags_list:
                tags.add(tag)
    
    application_counts = Counter()
    for application in Application.objects.all():
        try:
            industries = application.vacancy.tags_ai.get("tags", {}).get("industry", [])
        except Exception:
            continue
        for industry in industries:
            application_counts[industry] += 1
    top_categories = [tag for tag, count in application_counts.most_common(3)]
    
    context = {"vacancies": vacancies_context, "tags": tags, "top_categories": top_categories}
    return render(request, 'main/index.html', context)

@anonymous_required
def login_view(request):
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")
        is_company = request.POST.get("CompanyLoginCheckbox") == "on"
        print(password)
        
        backend = 'RecruitHelper.backends.UserAuthBackend'

        if is_company:
            user = authenticate(request, company_email=email, password=password)
        else:
            user = authenticate(request, email=email, password=password)
        print(user)
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
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                user = User.objects.create_user(
                    email=data["email"],
                    password=data["password"],
                    main_name=data["main_name"],
                    role="company" if is_company else "user"
                )
                if is_company:
                    Company.objects.create(user=user)
                else:
                    CUser.objects.create(user=user)
                authenticated_user = authenticate(request, email=data["email"], password=data["password"])
                if authenticated_user is None:
                    raise ValidationError('Ошибка аутентификации нового пользователя')
                login(request, authenticated_user)
                return redirect('/')
        except ValidationError as e:
            context = {'error': e.messages, 'is_company': is_company, 'form': UserRegistrationForm()}
            return render(request, 'auth/registration.html', context)
    context = {'form': UserRegistrationForm()}
    return render(request, 'auth/registration.html', context)

@login_required
def logout_view(request):
    logout(request)
    return redirect('home')

def company(request, company_id):
    context = {"company_object": Company.objects.filter(id=company_id)}
    return render(request, 'users/HRpage.html', context)

@login_required
def profile(request):
    user = request.user 
    context = {
        'user': user,
    }
    return render(request, 'users/profile.html',context)

@login_required
def profile_vacancies(request):
    context = {}
    return render(request, 'users/profile_vacancies.html', context)

@login_required
def profile_applications(request):
    context = {}
    return render(request, 'users/profile_applications.html', context)

def candidate(request, user_id):
    candidate_user = get_object_or_404(CUser, id=user_id)
    context = {
        'candidate': candidate_user
    }
    return render(request, 'users/candidatepage.html',context)

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
    vacancies_list = list(vacancies)
    
    tags_by_category = defaultdict(set)
    for vacancy in vacancies_list:
        try:
            ai_tags = vacancy.tags_ai.get("tags", {})
        except Exception:
            continue
        for category, tags_list in ai_tags.items():
            for tag in tags_list:
                tags_by_category[category].add(tag)
    tags_by_category = {cat: list(tags) for cat, tags in tags_by_category.items()}
    
    tags = set()
    for vacancy in vacancies_list:
        try:
            ai_tags = vacancy.tags_ai.get("tags", {})
        except Exception:
            continue
        for _, tags_list in ai_tags.items():
            for tag in tags_list:
                tags.add(tag)
    context = {"form": form, "vacancies": vacancies_list, "tags_by_category": tags_by_category, "tags": tags}
    return render(request, 'vacancies/vacancy_list.html', context)

def user_pendings(request):
    context = {}
    return render(request, 'user_pendings.html', context)

@login_required
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
    # is_applied = Application.objects.filter(vacancy=vacancy, candidate=request.user).exists()
    return render(request, 'vacancies/vacancy_detail.html', {'vacancy': vacancy})

@login_required
def apply_to_vacancy(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    application = Application.objects.create(
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
        application.ai_rating = int(response_data['rating'])

    except Exception as e:
        print(f"AI бунтует! Произошла ошибка {e}.")
        application.ai_rating = 0
    application.save()

    Notification.objects.create(
        user=vacancy.company,
        company=vacancy.company,
        notification_type='application',
        title=f'Новая заявка на вакансию: {vacancy.title}',
        vacancy=vacancy,
        is_read=False
    )

    return redirect('profile')

def privacy(request):
    return render(request, 'info/privacy_policy.html')

def news(request):
    return render(request, 'vacancies/news.html')

def about_us(request):
    context = { }
    return render(request, 'info/about_us.html', context)




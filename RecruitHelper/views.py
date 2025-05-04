from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from .models import *
from .forms import *
from django.core.exceptions import ValidationError
from .decorators import anonymous_required
from django.contrib.auth.decorators import login_required, user_passes_test
import random
from .chatgpt import ChatGPT
from . import prompts
import os
import json
from collections import defaultdict, Counter

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
        
        backend = 'RecruitHelper.backends.UserAuthBackend'
        
        user = authenticate(request, email=email, password=password, check_company=is_company)
        if user is not None:
            login(request, user)
            return redirect("home")
        else:
            return render(request, "auth/login.html", {"messages": "Неверный email или пароль"})

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
def edit_user(request):
    context = {}
    if request.method == 'POST':
        base_form = EditUserForm(request.POST, request.FILES, instance=request.user)
        if request.user.role == 'user':
            user_form = EditCUserForm(request.POST, request.FILES, instance=request.user.cuser)
        else:
            user_form = EditCompanyForm(request.POST, request.FILES, instance=request.user.company)
        if base_form.is_valid() and user_form.is_valid():
            base_form.save()
            user_form.save()
            return redirect('profile')
    else:
        base_form = EditUserForm(instance=request.user)
        if request.user.role == 'user':
            cuser_form = EditCUserForm(instance=request.user.cuser)
            context = {
                'base_form': base_form,
                'cuser_form': cuser_form,
            }
        elif request.user.role == 'company':
            company_form = EditCompanyForm(instance=request.user.company)
            context = {
                'base_form': base_form,
                'company_form': company_form,
            }
    return render(request, 'users/profileedit.html', context)

@login_required
def profile_vacancies(request):
    context = {}
    return render(request, 'users/profile_vacancies.html', context)

@login_required
def applications(request):
    if request.user.role == 'company':
        company = Company.objects.get(user=request.user)
        applications = Application.objects.filter(vacancy__company=company)
        context = {
            'applications': applications,
        }
    else:
        cuser = CUser.objects.get(user=request.user)
        applications = Application.objects.filter(candidate=cuser)
        context = {
            'applications': applications
        }
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        if application_id:
            try:
                application = Application.objects.get(id=application_id)
                if request.user.role == 'company' and application.vacancy.company.user == request.user:
                    application.status = 'accepted'
                    application.save()
                    chat = Chat.objects.create(id=application.vacancy.id,
                                        user=application.candidate,
                                        company=request.user.company,
                                        name=application.vacancy.title,
                                        vacancy=application.vacancy)
            except Application.DoesNotExist:
                pass
        return redirect('applications')
    return render(request, 'users/applications.html', context)

def candidate(request, user_id):
    candidate_user = get_object_or_404(User, id=user_id)
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

@login_required
@user_passes_test(lambda u: u.role == 'company')
def add_vacancy(request):
    form = VacancyForm()
    if request.method == 'POST':
        form = VacancyForm(request.POST)
        if form.is_valid():
            try:
                company = Company.objects.get(user=request.user)
                vacancy = Vacancy(
                    title=form.cleaned_data['title'],
                    description=form.cleaned_data['description'],
                    geography=form.cleaned_data['geography'],
                    company=company
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
                    vacancy.tags_ai = {}

                vacancy.save()
                request.user.company.vacancies.add(vacancy)
                request.user.save()

                return redirect('vacancies_list')
            except Company.DoesNotExist:
                print('Компания не найдена')
    return render(request, 'vacancies/add_vacancy.html', {'form': form})

@login_required
def vacancy(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    if request.user.role == 'user':
        is_applied = Application.objects.filter(vacancy=vacancy, candidate=request.user.cuser).exists()
    else:
        is_applied = True
    return render(request, 'vacancies/vacancy_detail.html', {'vacancy': vacancy, 'is_applied': is_applied})

@login_required
@user_passes_test(lambda u: u.role == 'user')
def apply_to_vacancy(request, vacancy_id):
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    application = Application.objects.create(
        vacancy=vacancy,
        candidate=request.user.cuser
    )
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        client = ChatGPT(
            api_key=api_key,
        )
        content = f"Вакансия: {vacancy.description}\n\nРезюме кандидата: {request.user.cuser.resume + request.user.description}"
        response_text = client.get_response(prompts.JOB_RANKING_CANDIDATE, content)
        print(response_text)
        response_data = json.loads(response_text)
        application.ai_rating = int(response_data['rating'])

    except Exception as e:
        print(f"AI бунтует! Произошла ошибка {e}.")
        application.ai_rating = 0
    application.save()

    Notification.objects.create(
        user=vacancy.company.user,
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

@login_required
@user_passes_test(lambda u: u.role == 'user')
def upload_resume(request):
    if request.method == 'POST':
        resume_file = request.FILES.get('resume')
        if resume_file:
            cuser = CUser.objects.get(user=request.user)
            cuser.resume = resume_file
            cuser.save()
            return redirect('profile')
    return redirect('profile')


def chats(request):
    if request.user.is_authenticated:
        user = request.user
        if user.role == 'company':
            chats = Chat.objects.filter(company=user.company)
        else:
            chats = Chat.objects.filter(user=user.cuser)
    else:
        chats = []

    return render(request, 'users/chats.html', {'chats': chats})

@login_required
def chat(request, chat_id):
    chat = Chat.objects.get(id=chat_id)
    messages = []
    for message in chat.messages.all():
        messages.append(message)
    context = {'messages': messages}
    return render(request, 'vacancies/chat.html', context)

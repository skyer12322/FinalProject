"""
Модуль с представлениями (views) для приложения RecruitHelper.
"""
import logging
import random
import os
import json
from collections import defaultdict, Counter
from django.db.models import Q
from django.db.models.functions import Cast
from django.db.models import TextField
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from django.http import FileResponse, JsonResponse
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages as dj_messages
from django.contrib.auth import login, authenticate, logout
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.cache import cache_page
from django.views.decorators.vary import vary_on_cookie
from django.core.cache import cache
from RecruitHelper.models import (
    User, Company, Vacancy, Application, Chat, CUser, Notification
)
from RecruitHelper.forms import (
    UserRegistrationForm, VacancyForm, EditUserForm, EditCUserForm, EditCompanyForm
)
from .decorators import anonymous_required, cache_per_user
from .chatgpt import ChatGPT
from . import prompts

logger = logging.getLogger(__name__)

@login_required
@user_passes_test(lambda u: u.role == 'company')
def edit_vacancy(request, vacancy_id):
    """
    Редактирование вакансии пользователем-компанией (только для владельца вакансии).
    """
    vacancy_obj = get_object_or_404(Vacancy, id=vacancy_id)
    if not vacancy_obj.company or vacancy_obj.company.user != request.user:
        return redirect('profile_vacancies')

    if request.method == 'POST':
        form = VacancyForm(request.POST, instance=vacancy_obj)
        if form.is_valid():
            vacancy_obj = form.save(commit=False)

            tags = {
                'specialization': list(request.POST.get('specialization', '').split(',')),
                'occupancy': list(request.POST.get('occupancy', '').split(',')),
                'position': list(request.POST.get('position', '').split(',')),
                'tech': list(request.POST.get('tech', '').split(',')),
                'industry': list(request.POST.get('industry', '').split(',')),
            }
            tags = {k: [t for t in v if t] for k, v in tags.items()}
            vacancy_obj.tags_ai = tags

            vacancy_obj.save()
            return redirect('vacancy', vacancy_id=vacancy_obj.id)
    else:
        form = VacancyForm(instance=vacancy_obj)

    context = {'form': form, 'vacancy': vacancy_obj}
    return render(request, 'vacancies/edit_vacancy.html', context)

@login_required
def notifications(request):
    """
    Центр уведомлений пользователя: просмотр, отметка прочитанным.
    """
    if request.method == 'POST':
        action = request.POST.get('action')
        notification_id = request.POST.get('notification_id')

        if action == 'mark_all_read':
            Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)
            return redirect('notifications')

        if action == 'mark_read' and notification_id:
            Notification.objects.filter(id=notification_id, user=request.user).update(is_read=True)
            return redirect('notifications')

    notifications_qs = Notification.objects.filter(user=request.user).select_related('vacancy', 'chat').order_by('-created_at')
    unread_count = notifications_qs.filter(is_read=False).count()
    return render(
        request,
        'users/notifications.html',
        {
            'notifications': notifications_qs,
            'unread_count': unread_count,
        },
    )

@cache_per_user(60 * 15)
def home(request):
    """
    Отображает главную страницу с вакансиями, тегами и популярными категориями.

    :param request: Объект запроса Django.
    :return: Объект HttpResponse с отрендеренной HTML-страницей.
    """
    logger.info("Home page request received")
    vacancies_context = []
    vacancy_count = Vacancy.objects.count()
    logger.info("Taking 4 vacancies... ")
    if vacancy_count > 4:
        vacancy_ids = list(Vacancy.objects.values_list('id', flat=True))
        random_ids = random.sample(vacancy_ids, 4)
        for vacancy_id in random_ids:
            vacancy = Vacancy.objects.get(id=vacancy_id)
            vacancies_context.append(vacancy)
        logger.info("Successfully retrieved 4 random vacancies")
    else:
        vacancies_context = Vacancy.objects.all()
        logger.info(f"Returned all {vacancy_count} vacancies as count <=4")
    tags = set()
    for vacancy in Vacancy.objects.all():
        try:
            ai_tags = vacancy.tags_ai.get("tags", {})
        except Exception as e:
            logger.warning(f"Failed to get tags for vacancy {vacancy.id}: {str(e)}")
            continue
        for _, tags_list in ai_tags.items():
            for tag in tags_list:
                tags.add(tag)
    application_counts = Counter()
    for application in Application.objects.all():
        try:
            tags_dict = application.vacancy.tags_ai if isinstance(application.vacancy.tags_ai, dict) else {}
            industries = tags_dict.get("industry") if isinstance(tags_dict.get("industry"), list) else []
        except Exception as e:
            logger.warning(f"Error counting applications by industry: {str(e)}")
            continue
        for industry in industries:
            if industry:
                application_counts[industry] += 1

    def pick_icon(name: str) -> str:
        lowered = (name or "").lower()
        if any(k in lowered for k in ("it", "айти", "dev", "разработ", "software", "програм")):
            return "💻"
        if any(k in lowered for k in ("финанс", "банк", "account", "audit", "бух")):
            return "💰"
        if any(k in lowered for k in ("sales", "продаж", "bizdev", "аккаунт")):
            return "📈"
        if any(k in lowered for k in ("инжен", "engineer", "hardware", "мех", "элект")):
            return "⚙️"
        if any(k in lowered for k in ("hr", "рекрут", "кадр")):
            return "🧑‍💼"
        if any(k in lowered for k in ("маркет", "marketing", "smm", "pr")):
            return "📣"
        return "🏷️"

    vacancy_list_for_counts = list(Vacancy.objects.all())
    vacancy_industry_counts = Counter()
    for v in vacancy_list_for_counts:
        tags_dict = v.tags_ai if isinstance(v.tags_ai, dict) else {}
        industry_tags = tags_dict.get("industry") if isinstance(tags_dict.get("industry"), list) else []
        for tag in industry_tags:
            if tag:
                vacancy_industry_counts[tag] += 1

    # Prefer "popular by applications", fallback to "popular by vacancies",
    # fallback to a stable default list so the block is never empty.
    top_categories = [tag for tag, _ in application_counts.most_common(6)]
    if not top_categories:
        top_categories = [tag for tag, _ in vacancy_industry_counts.most_common(6)]
    if not top_categories:
        top_categories = ["IT и разработка", "Финансы", "Продажи", "Инженерия"]

    popular_categories = []
    for category_name in top_categories:
        popular_categories.append(
            {
                "name": category_name,
                "icon": pick_icon(category_name),
                "count": vacancy_industry_counts.get(category_name, 0),
            }
        )

    context = {
        "vacancies": vacancies_context,
        "tags": tags,
        "popular_categories": popular_categories,
    }
    return render(request, 'main/index.html', context)

@anonymous_required
def login_view(request):
    """
    Обрабатывает вход пользователей в систему.

    :param request: Объект запроса Django.
    :return: Объект HttpResponse с отрендеренной HTML-страницей
    (перенаправление или страница логина с ошибкой).
    """
    logger.info("Login page request received")
    logger.debug("Processing login request")
    if request.method == "POST":
        email = request.POST.get("username")
        password = request.POST.get("password")
        is_company = request.POST.get("CompanyLoginCheckbox") == "on"
        logger.info(f"Login attempt for user: {email}, company: {is_company}")
        user = authenticate(request, email=email, password=password, check_company=is_company)
        if user is not None:
            login(request, user)
            logger.info(f"Successful login for user: {email}")
            return redirect("home")
        logger.warning(
            f'''Failed login attempt for user: {email}. Reason:
            {'Invalid credentials' if user is None else 'Other error'}''')
        dj_messages.error(request, "Неверный email или пароль")
        return render(request, "auth/login.html")
    return render(request, "auth/login.html")

@anonymous_required
def register(request):
    """
    Обрабатывает регистрацию новых пользователей (соискателей или компаний).

    :param request: Объект запроса Django.
    :return: Объект HttpResponse с отрендеренной HTML-страницей
    (перенаправление или страница регистрации с ошибкой).
    """
    logger.info("Registration page request received")
    logger.debug("Processing registration request")
    if request.method == 'POST':
        is_company = 'CompanyRegistrationCheckbox' in request.POST
        try:
            form = UserRegistrationForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                logger.info(
                    f'''Registering new user: {data['email']},
                    role: {'company' if is_company else 'user'}''')

                user = User.objects.create_user(
                    email=data["email"],
                    password=data["password"],
                    main_name=data["main_name"],
                    role="company" if is_company else "user")
                if is_company:
                    Company.objects.create(user=user)
                else:
                    CUser.objects.create(user=user)

                authenticated_user = authenticate(request,
                                                  email=data["email"],
                                                  password=data["password"])
                if authenticated_user is None:
                    logger.error("New user authentication failed")
                    raise ValidationError('New user authentication failed')
                login(request, authenticated_user)
                logger.info(f"Successful registration and login for user: {data['email']}")
                return redirect('/')
        except ValidationError as e:
            logger.error(f"Registration validation error: {str(e)}")
            context = {'error': e.messages,
                       'is_company': is_company,
                       'form': UserRegistrationForm()}
            return render(request, 'auth/registration.html', context)
    context = {'form': UserRegistrationForm()}
    return render(request, 'auth/registration.html', context)

@login_required
def logout_view(request):
    """
    Выполняет выход текущего пользователя из системы.

    :param request: Объект запроса Django.
    :return: Объект HttpResponse (перенаправление на главную страницу).
    """
    logger.info(f"User logging out: {request.user.email}")
    logout(request)
    return redirect('home')

def company(request, company_id):
    cache_key = f'company_{company_id}'
    result = cache.get(cache_key)
    if result:
        return result
    """
    Отображает страницу компании по её ID.

    :param request: Объект запроса Django.
    :param company_id: ID компании.
    :return: Объект HttpResponse с отрендеренной HTML-страницей.
    """
    logger.info("Company page request received")
    logger.debug(f"Requesting company page ID: {company_id}")
    company_obj = get_object_or_404(Company, id=company_id)
    context = {"company": company_obj}
    result = render(request, 'users/HRpage.html', context)
    cache.set(cache_key, result, 60 * 30)
    return result

@login_required
def profile(request):
    cache_key = f'profile_{request.user.id}'
    result = cache.get(cache_key)
    if result:
        return result
    """
    Отображает страницу профиля текущего пользователя.

    :param request: Объект запроса Django.
    :return: Объект HttpResponse с отрендеренной HTML-страницей.
    """
    logger.info("Profile page request received")
    logger.debug(f"Profile request for user: {request.user.email}")
    user = request.user
    context = {'user': user}
    result = render(request, 'users/profile.html', context)
    cache.set(cache_key, result, 60 * 10)
    return result

@login_required
def profile_vacancies(request):
    cache_key = f'profile_vacancies_{request.user.id}'
    result = cache.get(cache_key)
    if result:
        return result
    """
    Отображает вакансии, созданные текущим пользователем (для компаний).

    :param request: Объект запроса Django.
    :return: Объект HttpResponse с отрендеренной HTML-страницей.
    """
    logger.info("Vacancies for current user page request received")
    logger.debug(f"Profile vacancies request for user: {request.user.email}")
    vacancies = Vacancy.objects.filter(company=request.user.company)
    context = {'vacancies': vacancies}
    result = render(request, 'users/vacancies.html', context)
    cache.set(cache_key, result, 60 * 5)
    return result

@login_required
def edit_user(request):
    """
    Обрабатывает редактирование профиля текущего пользователя.

    :param request: Объект запроса Django.
    :return: Объект HttpResponse с отрендеренной HTML-страницей
    (перенаправление или страница редактирования с ошибками).
    """
    logger.info("User edit page request received")
    logger.debug(f"Edit profile request for user: {request.user.email}")
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
            logger.info(f"User profile updated successfully: {request.user.email}")
            return redirect('profile')
        logger.warning(f"Profile update validation errors: {base_form.errors} {user_form.errors}")
    else:
        base_form = EditUserForm(instance=request.user)
        if request.user.role == 'user':
            cuser_form = EditCUserForm(instance=request.user.cuser)
            context = {'base_form': base_form, 'cuser_form': cuser_form}
        elif request.user.role == 'company':
            company_form = EditCompanyForm(instance=request.user.company)
            context = {
                'base_form': base_form,
                'company_form': company_form,
            }
    return render(request, 'users/profileedit.html', context)

@login_required
def applications(request):
    """
    Отображает список заявок на вакансии для текущего пользователя (соискателя или компании).

    :param request: Объект запроса Django.
    :return: Объект HttpResponse с отрендеренной HTML-страницей.
    """
    logger.info("Applications for current user page request received")
    logger.debug(f"Applications request for user: {request.user.email}")
    if request.user.role == 'company':
        company = Company.objects.get(user=request.user)
        applications = Application.objects.filter(vacancy__company=company)
        context = {'applications': applications}
    else:
        cuser = CUser.objects.get(user=request.user)
        applications = Application.objects.filter(candidate=cuser)
        context = {
            'applications': applications
        }
    if request.method == 'POST':
        application_id = request.POST.get('application_id')
        action = request.POST.get('action')
        if application_id and action:
            try:
                application = Application.objects.get(id=application_id)
                if request.user.role=='company' and application.vacancy.company.user==request.user:
                    if action == 'approve':
                        application.status = 'accepted'
                        application.save()
                        Chat.objects.get_or_create(
                            user=application.candidate,
                            company=request.user.company,
                            vacancy=application.vacancy,
                            defaults={'name': application.vacancy.title}
                        )
                    elif action == 'reject':
                        application.status = 'rejected'
                        application.save()
            except Application.DoesNotExist:
                pass
        return redirect('applications')
    return render(request, 'users/applications.html', context)

def candidate(request, user_id):
    cache_key = f'candidate_{user_id}'
    result = cache.get(cache_key)
    if result:
        return result
    """
    Отображает страницу кандидата по ID пользователя.

    :param request: Объект запроса Django.
    :param user_id: ID пользователя-кандидата.
    :return: Объект HttpResponse с отрендеренной HTML-страницей.
    """
    logger.info("Candidate page request received")
    logger.debug(f"Requesting candidate page ID: {user_id}")
    candidate_user = get_object_or_404(User, id=user_id)
    context = {'user': candidate_user}
    result = render(request, 'users/candidatepage.html', context)
    cache.set(cache_key, result, 60 * 30)
    return result

def vacancies(request):
    # Note: this page supports GET search params (q/location),
    # so we intentionally do not cache the rendered response globally.
    """
    Отображает список всех вакансий с возможностью фильтрации.

    :param request: Объект запроса Django.
    :return: Объект HttpResponse с отрендеренной HTML-страницей.
    """
    logger.info("Vacancies page request received")
    logger.debug("Vacancies list request")
    q = (request.GET.get('q') or '').strip()
    location = (request.GET.get('location') or '').strip()
    industry = (request.GET.get('industry') or '').strip()

    vacancies_qs = Vacancy.objects.all()
    if q:
        vacancies_qs = vacancies_qs.filter(
            Q(title__icontains=q) | Q(description__icontains=q)
        )
    if location:
        vacancies_qs = vacancies_qs.annotate(
            geography_text=Cast('geography', TextField())
        ).filter(geography_text__icontains=location)

    vacancies_list = list(vacancies_qs)
    if industry:
        industry_lower = industry.casefold()
        filtered = []
        for v in vacancies_list:
            tags_dict = v.tags_ai if isinstance(v.tags_ai, dict) else {}
            industry_tags = tags_dict.get("industry") if isinstance(tags_dict.get("industry"), list) else []
            if any((t or "").casefold() == industry_lower for t in industry_tags):
                filtered.append(v)
        vacancies_list = filtered
    logger.info(f"Found {len(vacancies_list)} vacancies after filtering")
    tags_by_category = {
        'specialization': set(),
        'occupancy': set(),
        'position': set(),
        'tech': set(),
        'industry': set()
    }
    for vacancy in vacancies_list:
        try:
            if isinstance(vacancy.tags_ai, dict):
                for category, tags in vacancy.tags_ai.items():
                    if category in tags_by_category and isinstance(tags, list):
                        tags_by_category[category].update(tags)
        except Exception as e:
            logger.warning(f"Failed to process tags for vacancy {vacancy.id}: {str(e)}")
            continue
    tags_by_category = {k: sorted(list(v)) for k, v in tags_by_category.items()}
    max_salary = max((v.max_salary for v in vacancies_list if v.max_salary is not None), default=0)
    min_salary = min((v.min_salary for v in vacancies_list if v.min_salary is not None), default=0)
    
    context = {
        "vacancies": vacancies_list,
        "tags_by_category": tags_by_category,
        "max_salary": max_salary,
        "min_salary": min_salary,
        "q": q,
        "location": location,
        "industry": industry,
    }
    return render(request, 'vacancies/vacancy_list.html', context)

@login_required
@user_passes_test(lambda u: u.role == 'company')
def add_vacancy(request):
    """
    Обрабатывает создание новой вакансии пользователем-компанией.

    :param request: Объект запроса Django.
    :return: Объект HttpResponse с отрендеренной HTML-страницей
    (перенаправление или страница добавления вакансии с ошибками).
    """
    logger.info("Vacancy creation page request received")
    logger.debug(f"Add vacancy request from user: {request.user.email}")
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
                    company=company,
                    min_salary=form.cleaned_data['min_salary'],
                    max_salary=form.cleaned_data['max_salary'],
                    currency=form.cleaned_data['currency']
                    )
                try:
                    api_key = os.environ.get("OPENAI_API_KEY")
                    client = ChatGPT(api_key=api_key)
                    response_text = client.get_response(prompts.JOB_RANKING + f'\nЗарплата: {vacancy.min_salary} - {vacancy.max_salary} {vacancy.currency}', vacancy.description)
                    vacancy.ai_rating = int(response_text['rating'])
                    tags = {
                        'specialization': list(request.POST.get('specialization').split(',')),
                        'occupancy': list(request.POST.get('occupancy').split(',')),
                        'position': list(request.POST.get('position').split(',')),
                        'tech': list(request.POST.get('tech').split(',')),
                        'industry': list(request.POST.get('industry').split(','))
                    }
                    empty_fields = [key for key, elem in tags.items() if elem == ['']]
                    if empty_fields:
                        tags_text_raw = client.get_response(prompts.TAGS_ASSIGN, f'{vacancy.title}\nОтсутствуют теги {empty_fields}\n{vacancy.description}')
                        try:
                            if isinstance(tags_text_raw, str):
                                tags_text_json = json.loads(tags_text_raw)
                            elif isinstance(tags_text_raw, dict):
                                tags_text_json = tags_text_raw
                            else:
                                raise ValueError("Unexpected response type from ChatGPT")
                            tags_ai = tags_text_json
                        except (json.JSONDecodeError, ValueError, TypeError) as e:
                            logger.error(f"Error processing TAGS_ASSIGN response: {str(e)}. Falling back to empty tags.")
                            tags_ai = {}
                    else:
                        tags_ai = {}
                    if tags_ai:
                        for elem in tags_ai['tags']:
                            tags[elem] = tags_ai['tags'][elem]
                    vacancy.tags_ai = tags
                    # tags_text is not guaranteed to exist; log the raw response instead.
                    logger.debug(f"ChatGPT tags response (raw): {tags_text_raw if 'tags_text_raw' in locals() else 'N/A'}")
                    logger.debug(f"ChatGPT response for rating: {response_text if 'response_text' in locals() else 'N/A'}")
                    logger.info(f"Successfully processed ChatGPT data for vacancy: {vacancy.title}")
                except Exception as e:
                    logger.error(f"ChatGPT processing error: {str(e)}")
                    vacancy.ai_rating = 0
                    vacancy.tags_ai = {}
                vacancy.save()
                request.user.company.vacancies.add(vacancy)
                request.user.save()
                logger.info(f"New vacancy created: {vacancy.title}")
                return redirect('vacancies_list')
            except Company.DoesNotExist:
                logger.critical("Attempt to create vacancy without company")
    return render(request, 'vacancies/add_vacancy.html', {'form': form})

@login_required
def vacancy(request, vacancy_id):
    """
    Отображает подробную страницу вакансии по её ID.

    :param request: Объект запроса Django.
    :param vacancy_id: ID вакансии.
    :return: Объект HttpResponse с отрендеренной HTML-страницей.
    """
    logger.info("Vacancy page request received")
    logger.debug(f"Requesting vacancy ID: {vacancy_id}")
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    if request.user.role == 'user':
        is_applied = Application.objects.filter(vacancy=vacancy,
                                                candidate=request.user.cuser).exists()
    else:
        is_applied = True
    return render(request, 'vacancies/vacancy_detail.html', {'vacancy': vacancy,
                                                             'is_applied': is_applied})

@login_required
@user_passes_test(lambda u: u.role == 'user')
def apply_to_vacancy(request, vacancy_id):
    """
    Обрабатывает подачу заявки пользователем на вакансию.

    :param request: Объект запроса Django.
    :param vacancy_id: ID вакансии.
    :return: Объект HttpResponse (перенаправление на страницу профиля).
    """
    logger.info(f"User applying to vacancy: {request.user.email} -> {vacancy_id}")
    vacancy = get_object_or_404(Vacancy, id=vacancy_id)
    application = Application.objects.create(vacancy=vacancy, candidate=request.user.cuser)
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        client = ChatGPT(api_key=api_key)
        content = f'''Vacancy: {vacancy.description}\n\n
        Candidate resume: {request.user.cuser.resume }
        Candidate description: {request.user.description}
        '''
        response_text = client.get_response(prompts.JOB_RANKING_CANDIDATE, content)
        logger.debug(f"ChatGPT response for candidate evaluation: {response_text}")
        response_data = json.loads(response_text)
        application.ai_rating = int(response_data['rating'])
    except Exception as e:
        logger.error(f"ChatGPT candidate evaluation error: {str(e)}")
        application.ai_rating = 0
    application.save()
    Notification.objects.create(
        user=vacancy.company.user,
        notification_type='application',
        title=f'New application for vacancy: {vacancy.title}',
        vacancy=vacancy,
        is_read=False)
    logger.info(
        f'''
    Notification created for company
    {vacancy.company.user.email}
    about new application''')
    logger.info(
        f"New application created for vacancy: {vacancy_id}")
    return redirect('profile')

@login_required
@user_passes_test(lambda u: u.role == 'user')
def upload_resume(request):
    """
    Обрабатывает загрузку резюме текущим пользователем.

    :param request: Объект запроса Django.
    :return: Объект HttpResponse (перенаправление на страницу профиля).
    """
    logger.debug(f"Resume upload request from user: {request.user.email}")
    if request.method == 'POST':
        resume_file = request.FILES.get('resume')
        if resume_file:
            cuser = CUser.objects.get(user=request.user)
            cuser.resume = resume_file
            cuser.save()
            logger.info(f"Resume uploaded successfully for user: {request.user.email}")
            return redirect('profile')
    return redirect('profile')

def privacy(request):
    cache_key = 'privacy_page'
    result = cache.get(cache_key)
    if result:
        return result
    """
    Отображает страницу политики конфиденциальности.

    :param request: Объект запроса Django.
    :return: Объект HttpResponse с отрендеренной HTML-страницей.
    """
    logger.info("Privacy policy page requested")
    result = render(request, 'info/privacy_policy.html')
    cache.set(cache_key, result, 60 * 60)
    return result

def terms(request):
    cache_key = 'terms_page'
    result = cache.get(cache_key)
    if result:
        return result
    """
    Отображает страницу условий использования.

    :param request: Объект запроса Django.
    :return: Объект HttpResponse с отрендеренной HTML-страницей.
    """
    result = render(request, 'info/terms_of_use.html')
    cache.set(cache_key, result, 60 * 60)
    return result

def news(request):
    cache_key = 'news_page'
    result = cache.get(cache_key)
    if result:
        return result
    """
    Отображает страницу новостей.

    :param request: Объект запроса Django.
    :return: Объект HttpResponse с отрендеренной HTML-страницей.
    """
    logger.info("News page requested")
    result = render(request, 'info/news.html')
    cache.set(cache_key, result, 60 * 30)
    return result

def about_us(request):
    cache_key = 'about_us_page'
    result = cache.get(cache_key)
    if result:
        return result
    """
    Отображает страницу "О нас".

    :param request: Объект запроса Django.
    :return: Объект HttpResponse с отрендеренной HTML-страницей.
    """
    logger.info("About us page requested")
    context = { }
    result = render(request, 'info/about_us.html', context)
    cache.set(cache_key, result, 60 * 30)
    return result

@api_view(['GET'])
@permission_classes([IsAdminUser])
def download_logs(request):
    """
    API endpoint для скачивания логов сервера (доступно только администраторам).

    :param request: Объект запроса Django.
    :return: Объект FileResponse с файлом логов или объект Response с ошибкой.
    """
    log_path = settings.LOG_FILE_PATH
    if not os.path.exists(log_path):
        return Response(
            {"error": "Файл логов не найден"},
            status=status.HTTP_404_NOT_FOUND
        )
    if not os.path.isfile(log_path):
        return Response(
            {"error": "Указанный путь не является файлом"},
            status=status.HTTP_400_BAD_REQUEST
        )
    try:
        return FileResponse(
            open(log_path, 'rb'),
            as_attachment=True,
            filename='server_logs.log'
        )
    except Exception as e:
        return Response(
            {"error": f"Ошибка при чтении файла: {str(e)}"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@login_required
def chats(request):
    """
    Отображает список чатов для текущего пользователя.

    :param request: Объект запроса Django.
    :return: Объект HttpResponse с отрендеренной HTML-страницей.
    """
    user = request.user
    if user.role == 'company':
        chats = Chat.objects.filter(company=user.company)
    else:
        chats = Chat.objects.filter(user=user.cuser)

    return render(request, 'users/chat_list.html', {'chats': chats})

@login_required
def chat(request, chat_id):
    """
    Отображает конкретный чат с сообщениями.

    :param request: Объект запроса Django.
    :param chat_id: ID чата.
    :return: Объект HttpResponse с отрендеренной HTML-страницей.
    """
    chat = get_object_or_404(Chat, id=chat_id)
    
    # Проверка прав доступа
    if request.user.role == 'company' and chat.company.user != request.user:
        return redirect('chats')
    elif request.user.role == 'user' and chat.user.user != request.user:
        return redirect('chats')
    
    # Получаем все чаты для сайдбара
    if request.user.role == 'company':
        chats = Chat.objects.filter(company=request.user.company)
    else:
        chats = Chat.objects.filter(user=request.user.cuser)
    
    return render(request, 'users/chat_interface.html', {'chat': chat, 'chats': chats})

@login_required
def chat_api(request, chat_id):
    """
    API endpoint для получения данных чата.

    :param request: Объект запроса Django.
    :param chat_id: ID чата.
    :return: JsonResponse с данными чата.
    """
    try:
        chat = Chat.objects.select_related(
            'company__user', 'user__user', 'vacancy'
        ).prefetch_related(
            'messages__user'
        ).get(id=chat_id)
        
        # Проверяем права доступа
        if request.user.role == 'company' and chat.company.user != request.user:
            return JsonResponse({'error': 'Access denied'}, status=403)
        elif request.user.role == 'user' and chat.user.user != request.user:
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        messages = [{
            'id': msg.id,
            'content': msg.content,
            'timestamp': msg.timestamp.isoformat(),
            'user_id': msg.user.id,
            'user_name': msg.user.main_name
        } for msg in chat.messages.all().order_by('timestamp')]
        
        return JsonResponse({
            'id': chat.id,
            'name': chat.name,
            'vacancy_title': chat.vacancy.title,
            'company_name': chat.company.user.main_name,
            'user_name': f"{chat.user.first_name} {chat.user.last_name}",
            'messages': messages
        })
    except Chat.DoesNotExist:
        return JsonResponse({'error': 'Chat not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

from django.http import JsonResponse
from .models import Vacancy, Company
import json

def filters_handler(request):
    """
    Обрабатывает запросы на фильтрацию вакансий.

    :param request: Объект запроса Django.
    :return: Объект JsonResponse с отфильтрованными вакансиями.
    """
    try:
        data = json.loads(request.GET.get("data", "{}"))
        
        # Создаем базовый QuerySet
        vacancies = Vacancy.objects.all()
        
        # Применяем фильтры
        if data.get('specialization'):
            vacancies = vacancies.filter(tags_ai__specialization__icontains=data['specialization'])
        if data.get('occupancy'):
            vacancies = vacancies.filter(tags_ai__occupancy__icontains=data['occupancy'])
        if data.get('position'):
            vacancies = vacancies.filter(tags_ai__position__icontains=data['position'])
        if data.get('tech'):
            vacancies = vacancies.filter(tags_ai__tech__icontains=data['tech'])
        if data.get('industry'):
            vacancies = vacancies.filter(tags_ai__industry__icontains=data['industry'])
        if data.get('min_salary'):
            vacancies = vacancies.filter(min_salary__gte=data['min_salary'])
        if data.get('max_salary'):
            vacancies = vacancies.filter(max_salary__lte=data['max_salary'])

        # Преобразуем QuerySet в список словарей
        vacancies_list = list(vacancies.values(
            'id',
            'title',
            'description',
            'geography',
            'min_salary',
            'max_salary',
            'ai_rating',
        ))
        
        # Добавляем информацию о компании и валюте
        for i in range(len(vacancies_list)):
            vacancy = vacancies[i]
            vacancies_list[i]['company'] = vacancy.company.user.main_name
            vacancies_list[i]['currency'] = vacancy.get_currency_display()

        context = {
            'status': 'ok',
            'data': {
                'vacancies': vacancies_list,
            },
        }
        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)

def search_handler(request):
    """
    Обрабатывает запросы на поиск вакансий.

    :param request: Объект запроса Django.
    :return: Объект JsonResponse с найденными вакансиями.
    """
    try:
        search = request.GET.get("data", "")
        if search != '':
            vacancies = Vacancy.objects.filter(title__icontains=search)
            vacancies = vacancies.union(Vacancy.objects.filter(description__icontains=search))
        else:
            vacancies = Vacancy.objects.all()
            
        vacancies_list = list(vacancies.values(
            'id',
            'title',
            'description',
            'geography',
            'min_salary',
            'max_salary',
            'ai_rating',
        ))
        
        for i in range(len(vacancies_list)):
            vacancy = vacancies[i]
            vacancies_list[i]['company'] = vacancy.company.user.main_name
            vacancies_list[i]['currency'] = vacancy.get_currency_display()

        context = {
            'status': 'ok',
            'data': {
                'vacancies': vacancies_list,
            },
        }
        return JsonResponse(context)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
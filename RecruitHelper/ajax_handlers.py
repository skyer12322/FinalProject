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
        
        has_filters = any([
            data.get('specialization', '').strip(),
            data.get('occupancy', '').strip(), 
            data.get('position', '').strip(),
            data.get('tech', '').strip(),
            data.get('industry', '').strip()
        ])
        print(data)
        print(has_filters)
        # Применяем фильтры зарплаты только если есть другие фильтры
        if has_filters:
            if data.get('min_salary') and str(data.get('min_salary')).strip():
                vacancies = vacancies.filter(min_salary__gte=int(data['min_salary']))
            if data.get('max_salary') and str(data.get('max_salary')).strip():
                vacancies = vacancies.filter(max_salary__lte=int(data['max_salary']))
            if data.get('specialization', '').strip():
                vacancies = vacancies.filter(tags_ai__specialization__contains=[data['specialization']])
            if data.get('occupancy', '').strip():
                vacancies = vacancies.filter(tags_ai__occupancy__contains=[data['occupancy']])
            if data.get('position', '').strip():
                vacancies = vacancies.filter(tags_ai__position__contains=[data['position']])
            if data.get('tech', '').strip():
                vacancies = vacancies.filter(tags_ai__tech__contains=[data['tech']])
            if data.get('industry', '').strip():
                vacancies = vacancies.filter(tags_ai__industry__contains=[data['industry']])
            
        vacancies = list(vacancies)
        print(vacancies)

        # Преобразуем в список словарей
        vacancies_list = []
        for vacancy in vacancies:
            vacancies_list.append({
                'id': vacancy.id,
                'title': vacancy.title,
                'description': vacancy.description,
                'geography': vacancy.geography,
                'min_salary': vacancy.min_salary,
                'max_salary': vacancy.max_salary,
                'ai_rating': vacancy.ai_rating,
                'company': vacancy.company.user.main_name,
                'currency': vacancy.get_currency_display(),
            })

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
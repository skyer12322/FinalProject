from django.http import JsonResponse
from .models import Vacancy, Company

def filters_handler(request):
    """
    Обрабатывает запросы на фильтрацию вакансий.

    :param request: Объект запроса Django.
    :return: Объект JsonResponse с отфильтрованными вакансиями.
    """
    filters = request.GET.get("filters", "")
    if filters != '':
        vacancies = Vacancy.objects.filter(tags_ai__icontains=filters)
    else:
        vacancies = Vacancy.objects.all()
    context = {
        'status': 'ok',
        'data': {
            'vacancies': vacancies,
        },
    }
    return JsonResponse(context)

def search_handler(request):
    """
    Обрабатывает запросы на поиск вакансий.

    :param request: Объект запроса Django.
    :return: Объект JsonResponse с найденными вакансиями.
    """
    print('1')
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
        vacancies_list[i]['company'] = vacancies[i].company.user.main_name
        vacancies_list[i]['currency'] = vacancies[i].get_currency_display()
    print(vacancies_list)
    context = {
        'status': 'ok',
        'data': {
            'vacancies': vacancies_list,
        },
    }
    return JsonResponse(context)
from django.http import JsonResponse
from .models import Vacancy

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
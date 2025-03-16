from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from RecruitHelper.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name='home'),
    path('vacancies/', vacancies, name='vacancies_list'),
    path('vacancies/add/', add_vacancy, name='add_vacancy'),
    path('vacancies/<int:vacancy_id>/', vacancy, name='vacancy'),
    path('profile/', profile, name='profile'),
    path('candidatepage/', candidate, name='candidatepage'),
    path('HR/', company, name="HRpage"),
    path('login/', login, name="login"),
    path('register/', register, name="register"),
    path('privacy/', privacy, name="privacy"),
    path('news/', news, name="news"),
]

# Добавляем статические файлы только в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

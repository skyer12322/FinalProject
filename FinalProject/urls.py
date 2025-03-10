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
    path('candidate/', candidate, name='candidate'),
    path('company/<int:company_id>/', company, name="company"),
    path('login/', login, name="login"),
    path('register/', register, name="register"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

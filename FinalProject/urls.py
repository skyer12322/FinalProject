from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from RecruitHelper.views import *
from RecruitHelper import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name='home'),
    path('vacancies/', views.vacancies_list, name='vacancies_list'),
    path('vacancies/add/', views.add_vacancy, name='add_vacancy'),
    path('vacancies/<int:vacancy_id>/', views.vacancy_detail, name='vacancy_detail'),
    path('profile/', views.profile, name='profile'),
    path('candidatepage/', views.candidatepage, name='candidatepage'),
    path('HR/', views.HR, name="HRpage"),
    path('login/', views.login, name="login"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

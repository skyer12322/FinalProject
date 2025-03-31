from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from RecruitHelper.views import home, vacancies, add_vacancy, profile, vacancy, candidate, company
from RecruitHelper.views import login_view, register, privacy, news, about_us, logout_view


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name='home'),
    path('vacancies/', vacancies, name='vacancies_list'),
    path('vacancies/add/', add_vacancy, name='add_vacancy'),
    path('vacancies/<int:vacancy_id>/', vacancy, name='vacancy'),
    path('profile/', profile, name='profile'),
    path('candidatepage/', candidate, name='candidatepage'),
    path('HR/<int:company_id>/', company, name="HRpage"),
    path('login/', login_view, name="login"),
    path('register/', register, name="register"),
    path('privacy/', privacy, name="privacy"),
    path('news/', news, name="news"),
    path('about/', about_us, name="about"),
    path('profile/logout/', logout_view, name="logout"),
]

# Добавляем статические файлы только в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

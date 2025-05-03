from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from RecruitHelper.views import home, vacancies, add_vacancy, profile, vacancy, candidate, company, terms
from RecruitHelper.views import login_view, register, privacy, news, about_us, logout_view, edit_user
from RecruitHelper.views import apply_to_vacancy, profile_vacancies, applications, upload_resume
from RecruitHelper.views import download_logs
from RecruitHelper.views import apply_to_vacancy, profile_vacancies, applications, upload_resume, chats, chat


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name='home'),
    path('vacancies/', vacancies, name='vacancies_list'),
    path('vacancies/add/', add_vacancy, name='add_vacancy'),
    path('vacancies/<int:vacancy_id>/', vacancy, name='vacancy'),
    path('profile/', profile, name='profile'),
    path('profile/edit/', edit_user, name='edit_user'),
    path('candidate/<int:user_id>/', candidate, name='candidate'),
    path('company/<int:company_id>/', company, name="company"),
    path('login/', login_view, name="login"),
    path('register/', register, name="register"),
    path('privacy/', privacy, name="privacy"),
    path('terms/', terms, name='terms'),
    path('news/', news, name="news"),
    path('about/', about_us, name="about"),
    path('profile/logout/', logout_view, name="logout"),
    path('profile/vacancies/', profile_vacancies, name='profile_vacancies'),
    path('profile/applications/', applications, name='applications'),
    path('apply/<int:vacancy_id>/', apply_to_vacancy, name='apply_to_vacancy'),
    path('upload_resume/', upload_resume, name='upload_resume'),
    path('api/download-logs/', download_logs, name='download-logs'),
    path('profile/chats/', chats, name='chats'),
    path('profile/chat/<int:chat_id>', chat, name='chat')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Добавляем статические файлы только в режиме разработки
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

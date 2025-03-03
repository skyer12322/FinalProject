from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from RecruitHelper.views import *


urlpatterns = [
    path('admin/', admin.site.urls),
    path("", home, name='home'),
    path("vacancies/", vacancies_list, name='vacancies_list'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

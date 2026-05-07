"""
Утилиты для управления кэшированием.
"""
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from RecruitHelper.models import User, Vacancy, Application, Company, CUser


def invalidate_cache(*keys):
    """Инвалидирует кэш по ключам."""
    for key in keys:
        cache.delete(key)
        try:
            cache.incr(f"{key}_version", delta=1)
        except ValueError:
            # Some cache backends (e.g. LocMemCache) raise if key is missing.
            cache.set(f"{key}_version", 2)


def get_cache_version(key):
    """Получает версию кэша."""
    version = cache.get(f'{key}_version')
    if version is None:
        cache.set(f'{key}_version', 1)
        return 1
    return version


@receiver([post_save, post_delete], sender=User)
def invalidate_user_cache(sender, instance, **kwargs):
    """Инвалидирует кэш при изменении пользователя."""
    cache.delete_many([
        f'home_user_{instance.id}',
        f'profile_{instance.id}',
        f'edit_user_{instance.id}',
    ])
    try:
        cache.incr("home_version", delta=1)
    except ValueError:
        cache.set("home_version", 2)


@receiver([post_save, post_delete], sender=Vacancy)
def invalidate_vacancy_cache(sender, instance, **kwargs):
    """Инвалидирует кэш при изменении вакансии."""
    cache.delete_many([
        'home_anonymous',
        'vacancies_list',
        f'vacancy_{instance.id}',
        f'profile_vacancies_{instance.company.user.id}',
    ])
    try:
        cache.incr("home_version", delta=1)
    except ValueError:
        cache.set("home_version", 2)

    try:
        cache.incr("vacancies_version", delta=1)
    except ValueError:
        cache.set("vacancies_version", 2)


@receiver([post_save, post_delete], sender=Application)
def invalidate_application_cache(sender, instance, **kwargs):
    """Инвалидирует кэш при изменении заявки."""
    cache.delete_many([
        f'applications_{instance.candidate.user.id}',
        f'applications_{instance.vacancy.company.user.id}',
    ])


@receiver([post_save, post_delete], sender=Company)
def invalidate_company_cache(sender, instance, **kwargs):
    """Инвалидирует кэш при изменении компании."""
    cache.delete(f'company_{instance.id}')


@receiver([post_save, post_delete], sender=CUser)
def invalidate_cuser_cache(sender, instance, **kwargs):
    """Инвалидирует кэш при изменении кандидата."""
    cache.delete(f'candidate_{instance.user.id}')

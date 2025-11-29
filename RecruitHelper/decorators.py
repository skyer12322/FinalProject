"""
Декораторы для приложения RecruitHelper.
"""
from functools import wraps
from django.shortcuts import redirect
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


def anonymous_required(view_func):
    """
    Декоратор, который перенаправляет аутентифицированных пользователей на главную страницу.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper


def cache_per_user(timeout):
    """
    Кэширует страницу отдельно для каждого пользователя.
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if request.user.is_authenticated:
                cache_key = f'{view_func.__name__}_user_{request.user.id}'
            else:
                cache_key = f'{view_func.__name__}_anonymous'
            
            version = cache.get(f'{view_func.__name__}_version', 1)
            result = cache.get(cache_key, version=version)
            
            if result is None:
                result = view_func(request, *args, **kwargs)
                cache.set(cache_key, result, timeout, version=version)
            
            return result
        return wrapper
    return decorator

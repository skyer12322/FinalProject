from django.shortcuts import redirect
from django.contrib.auth.decorators import user_passes_test


anonymous_required = user_passes_test(
    lambda user: not user.is_authenticated,
    login_url='/',
    redirect_field_name=None
)


def user_required(view_func):

    def check_user(user):
        return user.is_authenticated and not user.is_staff and not user.is_superuser
    
    actual_decorator = user_passes_test(
        check_user,
        login_url='/',
        redirect_field_name=None
    )
    
    def wrapper(request, *args, **kwargs):
        if not check_user(request.user):
            return redirect('/')
        return view_func(request, *args, **kwargs)
    
    return actual_decorator(view_func)

# Декоратор для компаний
def company_required(view_func):

    def check_company(user):
        return user.is_authenticated and getattr(user, 'is_company', False)
    
    actual_decorator = user_passes_test(
        check_company,
        login_url='/',
        redirect_field_name=None
    )
    
    def wrapper(request, *args, **kwargs):
        if not check_company(request.user):
            return redirect('/')
        return view_func(request, *args, **kwargs)
    
    return actual_decorator(view_func)
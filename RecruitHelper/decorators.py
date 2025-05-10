"""
Модуль с декораторами для приложения RecruitHelper.
"""
from django.contrib.auth.decorators import user_passes_test

anonymous_required = user_passes_test(
    lambda user: not user.is_authenticated,
    login_url='/',
    redirect_field_name=None
)
company_required = user_passes_test(
    lambda user: user.role == 'company',
    login_url='/',
    redirect_field_name=None
)
user_required = user_passes_test(
    lambda user: user.role == 'user',
    login_url='/',
    redirect_field_name=None
)

from django.contrib.auth.decorators import user_passes_test

anonymous_required = user_passes_test(
    lambda user: not user.is_authenticated,
    login_url='/',
    redirect_field_name=None
)
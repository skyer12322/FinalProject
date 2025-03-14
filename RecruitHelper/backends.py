from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from RecruitHelper.models import Company


class CustomAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=username)
            if user.check_password(password):
                return user
        except UserModel.DoesNotExist:
            try:
                hr_user = Company.objects.get(email=username)
                if hr_user.check_password(password):
                    return hr_user
            except Company.DoesNotExist:
                return None
        return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            try:
                return Company.objects.get(pk=user_id)
            except Company.DoesNotExist:
                return None
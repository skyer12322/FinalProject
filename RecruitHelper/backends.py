from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from RecruitHelper.models import Company, CUser


class CUserAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user = CUser.objects.get(email=email)
            if user.check_password(password):
                return user
        except CUser.DoesNotExist:
            return None
        
class CompanyAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            user = Company.objects.get(username=username)
            if user.check_password(password):
                return user
        except Company.DoesNotExist:
            return None

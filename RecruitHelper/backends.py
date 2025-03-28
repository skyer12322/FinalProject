from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .models import Company, CUser

class CUserAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        print("Trying CUser auth...")
        try:
            user = CUser.objects.get(email=email)
            if user.check_password(password):
                return user
        except CUser.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return CUser.objects.get(pk=user_id)    # Важно для поддержки сессии
        except CUser.DoesNotExist:
            return None

class CompanyAuthBackend(BaseBackend):
    def authenticate(self, request, company_email=None, password=None):
        print("Trying Company auth...")
        try:
            company = Company.objects.get(email=company_email)
            print(company.password, password)
            if company.check_password(password):
                return company
        except Company.DoesNotExist:
            return None
        
    def get_user(self, user_id):
        try:
            return Company.objects.get(pk=user_id)
        except Company.DoesNotExist:
            return None
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .models import User

class UserAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, check_company=False):
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            try:
                user = User.objects.get(main_name=email)
            except User.DoesNotExist:
                return None
        
        if user.check_password(password):
            if check_company:
                if user.role == "company":
                    return user
                else:
                    return None
            else:
                return user
        return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)    # Важно для поддержки сессии
        except User.DoesNotExist:
            return None
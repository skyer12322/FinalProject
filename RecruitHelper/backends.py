from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .models import User

class UserAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, check_company=False):
        print("Trying User auth...")
        try:
            user = User.objects.get(email=email)
            print(user.email)
            if user.check_password(password):
                if check_company:
                    if user.role == "company":
                        return user
                    else:
                        return None
                else:
                    return user
        except User.DoesNotExist:
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)    # Важно для поддержки сессии
        except User.DoesNotExist:
            return None
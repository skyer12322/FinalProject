"""
Модуль, содержащий бэкенды аутентификации для приложения.
"""
import logging
from django.contrib.auth.backends import BaseBackend
from .models import User

logger = logging.getLogger(__name__)


class UserAuthBackend(BaseBackend):
    """
    Пользовательский backend аутентификации Django.

    Аутентифицирует пользователей по email или main_name.
    """
    def authenticate(self, request, email=None, password=None, check_company=False):
        """
        Аутентифицирует пользователя.

        Ищет пользователя по email или main_name и проверяет пароль.

        :param request: Объект запроса Django.
        :param email: Email или main_name пользователя.
        :param password: Пароль пользователя.
        :param check_company: Флаг, указывающий, требуется ли аутентификация как компания.
        :return: Объект пользователя, если аутентификация успешна, иначе None.
        """
        logger.debug(f"Authentication attempt - email: {email}, check_company: {check_company}")

        try:
            user = User.objects.get(email=email)
            logger.debug(f"User found by email: {email}")
        except User.DoesNotExist:
            logger.debug(f"Email not found, trying username: {email}")
            try:
                user = User.objects.get(main_name=email)
                logger.debug(f"User found by username: {email}")
            except User.DoesNotExist:
                logger.warning(f"User not found by email or username: {email}")
                return None

        if not user.check_password(password):
            logger.warning(f"Invalid password for user: {email}")
            return None

        if check_company and user.role != "company":
            logger.warning(f"Non-company user attempting company login: {email}")
            return None

        logger.info(f"Successful authentication for: {email} (ID: {user.id})")
        return user

    def get_user(self, user_id):
        """
        Извлекает пользователя по его ID.

        Используется системой аутентификации Django.

        :param user_id: ID пользователя.
        :return: Объект пользователя, если найден, иначе None.
        """
        logger.debug(f"Fetching user by ID: {user_id}")
        try:
            user = User.objects.get(pk=user_id)
            logger.debug(f"User found by ID: {user_id}")
            return user
        except User.DoesNotExist:
            logger.warning(f"User not found by ID: {user_id}")
            return None
        except Exception as e:
            logger.error(f"Error fetching user ID {user_id}: {str(e)}")
            return None

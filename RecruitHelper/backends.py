import logging
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model
from .models import User

# Настройка логгера
logger = logging.getLogger(__name__)


class UserAuthBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, check_company=False):
        logger.debug(
            f"Попытка аутентификации пользователя: email={email}, "
            f"check_company={check_company}"
        )

        try:
            # Попытка найти пользователя по email
            user = User.objects.get(email=email)
            logger.debug(f"Пользователь найден по email: {email}")
        except User.DoesNotExist:
            logger.debug(f"Пользователь с email {email} не найден, пробуем по имени")
            try:
                # Попытка найти пользователя по имени (как fallback)
                user = User.objects.get(main_name=email)
                logger.debug(f"Пользователь найден по имени: {email}")
            except User.DoesNotExist:
                logger.warning(f"Пользователь не найден ни по email, ни по имени: {email}")
                return None

        # Проверка пароля
        if user.check_password(password):
            logger.debug("Пароль верный")

            # Проверка типа пользователя (если требуется)
            if check_company:
                if user.role == "company":
                    logger.info(
                        f"Успешная аутентификация компании: {user.email} "
                        f"(ID: {user.id})"
                    )
                    return user
                else:
                    logger.warning(
                        f"Пользователь {user.email} не является компанией, "
                        f"хотя ожидалась компания"
                    )
                    return None
            else:
                logger.info(
                    f"Успешная аутентификация пользователя: {user.email} "
                    f"(ID: {user.id})"
                )
                return user
        else:
            logger.warning(
                f"Неверный пароль для пользователя: {email} "
                f"(ID: {user.id if 'user' in locals() else 'неизвестен'})"
            )
            return None

    def get_user(self, user_id):
        logger.debug(f"Получение пользователя по ID: {user_id}")
        try:
            user = User.objects.get(pk=user_id)
            logger.debug(f"Пользователь с ID {user_id} найден")
            return user
        except User.DoesNotExist:
            logger.warning(f"Пользователь с ID {user_id} не найден")
            return None
        except Exception as e:
            logger.error(
                f"Ошибка при получении пользователя с ID {user_id}: {str(e)}"
            )
            return None
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    """
    Пользовательский менеджер пользователей для модели User.
    """
    def create_user(self, email, password=None, **extra_fields):
        """
        Создает и сохраняет пользователя с указанным email и паролем.

        :param email: Email пользователя.
        :param password: Пароль пользователя (опционально).
        :param extra_fields: Дополнительные поля пользователя.
        :return: Созданный объект User.
        :raises ValueError: Если email не указан.
        """
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

class User(AbstractBaseUser):
    """
    Базовая модель пользователя, от которой создаются другие варианты пользователя.

    Использует основное поле для логина - email, вторичное - main_name.
    """
    main_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    profile_image = models.FileField(upload_to='profile_images/', null=True, blank=True)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    role = models.CharField(
        max_length=20, 
        choices=[("user", "User"), ("company", "Company")], 
        default="user"
    )

    objects = CustomUserManager()

    USERNAME_FIELD = "email"

    def __str__(self):
        """
        Возвращает строковое представление пользователя (его email).

        :return: Email пользователя.
        """
        return self.email

class CUser(models.Model):
    """
    Модель рядового пользователя (работник), связанная один-к-одному с моделью User.
    """
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='cuser')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    user_vacancies = models.ManyToManyField("Vacancy", through='Application', related_name='candidates', blank=True)

    def __str__(self):
        """
        Возвращает строковое представление рядового пользователя (имя и фамилия).

        :return: Имя и фамилия рядового пользователя.
        """
        return f"{self.first_name} {self.last_name}"
    
class Company(models.Model):
    """
    Модель компании, связанная один-к-одному с моделью User.
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company')
    website = models.TextField(blank=True, null=True)

    def __str__(self):
        """
        Возвращает строковое представление компании (основное имя пользователя).

        :return: Основное имя пользователя компании.
        """
        return self.user.main_name

    
class Application(models.Model):
    """
    Модель заявки рядового пользователя на вакансию.
    """
    vacancy = models.ForeignKey('Vacancy', on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey("CUser", on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=[("pending", "Pending"), ("accepted", "Accepted"), ("rejected", "Rejected")], default="pending")
    ai_rating = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
        
    def __str__(self):
        """
        Возвращает строковое представление заявки.

        :return: Строковое представление заявки.
        """
        return f"{self.candidate} подал заявку на вакансию {self.vacancy}"

class Chat(models.Model):
    """
    Модель чата между рядовым пользователем и компанией по конкретной вакансии.
    """
    name = models.CharField(max_length=100)
    user = models.ForeignKey('CUser', related_name='chats', on_delete=models.SET_NULL, null=True)
    company = models.ForeignKey('Company', related_name='chats', on_delete=models.SET_NULL, null=True)
    messages = models.ManyToManyField('Message', related_name='chat', blank=True)
    vacancy = models.ForeignKey('Vacancy', on_delete=models.CASCADE, related_name='chats')

    def __str__(self):
        """
        Возвращает строковое представление чата (его ID).

        :return: Строковое представление чата.
        """
        return f"Chat {self.id}"
    
class Message(models.Model):
    """
    Модель сообщения в чате.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Возвращает строковое представление сообщения.

        :return: Строковое представление сообщения с указанием отправителя.
        """
        return f"User {self.user} : {self.content}"

    
class Vacancy(models.Model):
    """
    Модель вакансии.
    """
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    geography = models.JSONField(default=None, blank=True, null=True)
    ai_rating = models.PositiveIntegerField()
    tags_ai = models.JSONField(default=list, blank=True)
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name='vacancies', null=True, blank=True)
    def __str__(self):
        """
        Возвращает строковое представление вакансии (её название).

        :return: Название вакансии.
        """
        return self.title
    
class Notification(models.Model):
    """
    Модель уведомления для пользователей.
    """
    NOTIFICATION_TYPES = [
        ('application', 'Заявка'),
        ('message', 'Сообщение'),
        ('vacancy_update', 'Обновление вакансии'),
        ('system', 'Системное уведомление'),
    ]

    user = models.ForeignKey(User , on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=255)
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, null=True, blank=True, related_name='notifications')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        """
        Возвращает строковое представление уведомления.

        :return: Заголовок уведомления и его тип.
        """
        return f"{self.title} - {self.get_notification_type_display()}"
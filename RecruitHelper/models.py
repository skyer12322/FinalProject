from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class CUserManager(BaseUserManager):
    def create_user(self, email, phone, username, first_name, last_name, password=None, **extra_fields):
        if not username:
            raise ValueError('The username field must be set')
        if not first_name:
            raise ValueError('The first name field must be set')
        if not last_name:
            raise ValueError('The last name field must be set')
        if not email:
            raise ValueError('The email field must be set')
        if not phone:
            raise ValueError('The phone field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, phone=phone, username=username, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def get_user(self, user_id):
        try:
            return CUser.objects.get(pk=user_id)
        except CUser.DoesNotExist:
            return None
    
class CompanyManager(BaseUserManager):
    def create_user(self, email, company_name, phone, password=None, **extra_fields):
        if not company_name:
            raise ValueError('The company name field must be set')
        if not email:
            raise ValueError('The email field must be set')
        if not phone:
            raise ValueError('The phone field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, company_name=company_name, phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def get_user(self, user_id):
        try:
            return Company.objects.get(pk=user_id)
        except Company.DoesNotExist:
            return None

class ChatMessage(models.Model):
    user = models.IntegerField(default=-1)
    company = models.IntegerField(default=-1)
    content = models.TextField()
    
    def __str__(self):
        if self.user != -1:
            return f"User {self.user} : {self.content}"
        elif self.company != -1:
            return f"Company {self.company} : {self.content}"
    
class Chat(models.Model):
    messages = models.ManyToManyField(ChatMessage, related_name='chat', blank=True)
    
    def __str__(self):
        return f"Chat {self.id}"
    
class Vacancy(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    required_skills = models.JSONField()
    required_experience = models.PositiveIntegerField()
    required_education = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    geography = models.JSONField(default=None, blank=True, null=True)
    ai_rating = models.PositiveIntegerField()
    chat = models.ForeignKey(Chat, related_name="vacancy", null=True, blank=True, on_delete=models.SET_NULL)
    user = models.ForeignKey('CUser', related_name='vacancy_user', null=True, blank=True, on_delete=models.CASCADE)
    company = models.ForeignKey('Company', related_name='vacancy_company', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class CUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True)
    username = models.CharField(max_length=150, unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    profile_image = models.FileField(upload_to='profile_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    user_vacancies = models.ManyToManyField(Vacancy, through='Pendings', related_name='candidates', blank=True)
    chats = models.ManyToManyField(Chat, related_name='users', blank=True)
    
    objects = CUserManager()
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='cuser_groups',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='cuser_permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions',
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username', 'password']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Pendings(models.Model):
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE, related_name='pendings')
    candidate = models.ForeignKey(CUser, on_delete=models.CASCADE, related_name='pendings')
    ai_rating = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.candidate} подал заявку на вакансию {self.vacancy}"
    
class Company(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    company_name = models.CharField(max_length=255)
    date_created = models.DateTimeField(default=timezone.now)
    phone = models.CharField(max_length=15, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    vacancies = models.ManyToManyField(Vacancy, related_name='company', blank=True)
    chats = models.ManyToManyField(Chat, through='Vacancy', related_name='company', blank=True)

    objects = CompanyManager()

    groups = models.ManyToManyField(
        'auth.Group',
        related_name='company_groups',
        blank=True,
        help_text='The groups this company belongs to.',
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='company_permissions',
        blank=True,
        help_text='Specific permissions for this company.',
        verbose_name='user permissions',
    )
    
    vacancies = models.ManyToManyField(Vacancy, related_name='vacancy_companies', blank=True)
    chats = models.ManyToManyField(Chat, related_name='company_chats', blank=True)

    objects = CompanyManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['company_name, password']

    def __str__(self):
        return self.company_name
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class CUserManager(BaseUserManager):
    def create_user(self, email, username, first_name, last_name, password=None, **extra_fields):
        if not username:
            raise ValueError('The username field must be set')
        if not first_name:
            raise ValueError('The first name field must be set')
        if not last_name:
            raise ValueError('The last name field must be set')
        if not email:
            raise ValueError('The email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
class CompanyManager(BaseUserManager):
    def create_user(self, email, company_name, password=None, **extra_fields):
        if not company_name:
            raise ValueError('The company name field must be set')
        if not email:
            raise ValueError('The email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, company_name=company_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

class Tag(models.Model):
    name = models.CharField(max_length=255)
    
class Occupation(models.Model):
    name = models.CharField(max_length=255)

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
    tags = models.ManyToManyField('Tag', related_name='vacancies', blank=True)
    occupation = models.ManyToManyField(Occupation, related_name='vacancies', blank=True)

    def __str__(self):
        return self.title

class CUser(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    username = models.CharField(max_length=150, unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    profile_image = models.FileField(upload_to='profile_images/', null=True, blank=True)
    is_active = models.BooleanField(default=True)
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

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'email', 'password']

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

    USERNAME_FIELD = 'company_name'
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return self.company_name
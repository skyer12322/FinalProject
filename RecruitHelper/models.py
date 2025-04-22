from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

class User(AbstractBaseUser):
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
        return self.email

class CUser(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='cuser')
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=150)
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)
    user_vacancies = models.ManyToManyField("Vacancy", through='Application', related_name='candidates', blank=True)
    chats = models.ManyToManyField("Chat", related_name='users', blank=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"
    
class Company(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='company')
    chats = models.ForeignKey("Chat", related_name='company', blank=True, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.company_name
    
class Application(models.Model):
    vacancy = models.ForeignKey('Vacancy', on_delete=models.CASCADE, related_name='applications')
    candidate = models.ForeignKey("CUser", on_delete=models.CASCADE, related_name='applications')
    ai_rating = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
        
    def __str__(self):
        return f"{self.candidate} подал заявку на вакансию {self.vacancy}"
    
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
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    geography = models.JSONField(default=None, blank=True, null=True)
    ai_rating = models.PositiveIntegerField()
    tags_ai = models.JSONField(default=list, blank=True)
    company = models.ForeignKey("Company", on_delete=models.CASCADE, related_name='vacancies', null=True, blank=True)
    chats = models.ForeignKey("Chat", on_delete=models.CASCADE, related_name="vacancy", blank=True)

    def __str__(self):
        return self.title
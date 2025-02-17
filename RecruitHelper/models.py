from django.db import models
from django.contrib.auth.models import AbstractUser
import json

class Vacancy(models.Model):
    ''' Модель для вакансий '''
    title = models.CharField(max_length=255)                # Название вакансии
    description = models.TextField()                        # Описание вакансии
    required_skills = models.JSONField()                    # Требуемые навыки
    required_experience = models.PositiveIntegerField()     # Требуемый опыт (в годах)
    required_education = models.CharField(max_length=255)   # Требуемое образование
    created_at = models.DateTimeField(auto_now_add=True)    # Когда создано
    updated_at = models.DateTimeField(auto_now=True)        # Когда в последний раз обновили

    def __str__(self):
        return self.title


class CustomUser(AbstractUser):
    ''' Модель для пользователей, наследуемая от AbstractUser '''
    resume = models.FileField(upload_to='resumes/', null=True, blank=True)                              # Файл резюме
    favorite_hr = models.ManyToManyField('HRUser', related_name='favorite_candidates', blank=True)      # Избранные HR
    favorite_vacancies = models.ManyToManyField('Vacancy', related_name='favorited_by', blank=True)     # Избранные вакансии

    def __str__(self):
        return self.username

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class CandidateScore(models.Model):
    ''' Модель для хранения оценок кандидатов по вакансиям '''
    resume = models.ForeignKey(CustomUser, on_delete=models.CASCADE)    # Связь с моделью Resume
    vacancy = models.ForeignKey(Vacancy, on_delete=models.CASCADE)  # Связь с моделью Vacancy
    score = models.PositiveIntegerField()                           # Оценка соответствия кандидата вакансии
    matching_skills = models.JSONField()                            # JSON поле для хранения совпадающих навыков
    shortlisted = models.BooleanField(default=False)                # Флаг шорт листа
    evaluated_at = models.DateTimeField(auto_now_add=True)          # Дата оценки

    def __str__(self):
        return f"Score for {self.resume} on {self.vacancy}"


class HRUser(AbstractUser):
    ''' Модель для пользователей HR '''
    department = models.CharField(max_length=255)   # Отдел, в котором работает HR-специалист
    position = models.CharField(max_length=255)     # Должность HR-специалиста

    def __str__(self):
        return self.username


class Feedback(models.Model):
    ''' Модель для отзывов о резюме '''
    resume = models.ForeignKey(CustomUser, on_delete=models.CASCADE)    # Связь с моделью Resume
    hr_user = models.ForeignKey(HRUser, on_delete=models.CASCADE)   # Связь с моделью HRUser
    comment = models.TextField()                                    # Текстовый комментарий HR-специалиста
    created_at = models.DateTimeField(auto_now_add=True)            # Дата создания отзыва

    def __str__(self):
        return f"Feedback for {self.resume} by {self.hr_user}"

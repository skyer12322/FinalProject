# Найм работников при помощи ИИ

Cайт для поиска работы или сотрудников при помощи сервисов ИИ, потенциально аналог [hh.ru](https://hh.ru/). ИИ будет помогать в анализе резюме, ранжируя их от 0 до 10 с шагом 0.1 на основе требований вакансии и резюме кандидата. Тем самым значительно сокращается время для подбора сотрудников

## Технологии

На момент последнего `commit` в ветке `develop` используются следующие технологии:
- Python 3.12
- Django 5.1.6
- OpenAI 1.75.0
- python-dotenv 1.1.0
- requests 2.32.3
- whitenoise 6.9.0
- psycopg2-binary 2.9.0
- Docker
- PostgreSQL (by Supabase)


## Установка и запуск проекта

Что нужно для запуска проекта на момент последнего `commit` в ветке `develop`:
1. Создать виртуальное окружение `.venv`:
	```bash
	python -m venv .venv 
	```
2. Установите зависимости: 
	```bash
	pip install -r requirements.txt
	```
3. Создать и  выполнить миграции моделей:
	```bash
	python manage.py makemigrations
	```
	```bash
	python manage.py migrate
	```
4. Запустить сервер:
	```bash
	python manage.py runserver
	```


## Тестирование проекта
- ```python manage.py test RecruitHelper.tests``` -- для всех тестов
- ```python manage.py test RecruitHelper.tests.<название_файла>``` -- для конкретного файла тестов
### Файлы тестов:
-```test_models.py```\
-```test_views.py```\
-```test_forms.py```
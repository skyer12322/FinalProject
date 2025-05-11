# Найм работников при помощи ИИ

Cайт для поиска работы или сотрудников при помощи сервисов ИИ, потенциально аналог [hh.ru](https://hh.ru/). ИИ будет помогать как в анализе кандидата к вакансии, ранжируя их от 0 до 100 с шагом 1 на основе требований вакансии и резюме кандидата, так и в анализе вакансий, ранжируя их от 0 до 100 с шагом 1. Тем самым значительно сокращается как время поиска подходящей работы, так и отбора кандидатов на должность.

## ✨ Возможности

*   Анализ кандидатов на основе требований вакансии с использованием ИИ.
*   Анализ и ранжирование вакансий с помощью ИИ.
*   Значительное сокращение времени для поиска работы и отбора кандидатов.

## 🚀 Используемые технологии

Проект использует следующие технологии и библиотеки:

*   Python 3.12
*   CI/CD GitLab
*   Docker
*   PostgreSQL (через Supabase)
*   Django 5.1.6
*   OpenAI 1.75.0
*   python-dotenv 1.1.0
*   requests 2.32.3
*   whitenoise 6.9.0
*   psycopg2-binary 2.9.0

## ⚙️ Установка и подготовка к запуску

Чтобы запустить проект, следуйте этим шагам:

1.  Создайте виртуальное окружение `.venv`:

    ```bash
    python -m venv .venv
    ```

2.  Активируйте виртуальное окружение (команда зависит от ОС и оболочки):

    - **На Windows:**
      ```
      .venv\Scripts\activate
      ```
    - **На Linux/macOS:**
      ```
      source .venv/bin/activate
      ```
	

3.  Установите зависимости:

    ```bash
    pip install -r requirements.txt
    ```

4. Создайте свою базу данных из списка поддерживаеммых баз данных Django или зарегестрируйтесь на сервисе, который предоставляет базу данных

5. Создайте файл `.env`, и в нём пропишите переменные:

	```python
	DB_NAME="your_name"
	DB_USER="your_user"
	DB_PASSWORD="your_password"
	DB_HOST="your_host"
	DB_PORT="your_port" (ex. 1234)
	MAIN_HOSTs=["host1", "host2"] (если вы развёртываете веб-сервис на сервер)
	```

6.  Создайте и примените миграции базы данных:

    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

## ▶️ Запуск сервера

Запустите сервер разработки:

1. Для дебага, просмотра проекта и работой с wsgi-приложением:
	```bash
	python manage.py runserver
	```

2. Для развёртки и работы с asgi-приложением:
	```bash
	daphne FinalProject.asgi:application --port <your_port>
	```

## ✅ Запуск тестов

Чтобы запустить тесты проекта:

*   Запуск всех тестов:

    ```bash
    pytest --reuse-db --report=html
    ```

*   Запуск тестов для проверки покрытия тестирования:

    ```bash
    pytest --reuse-db --cov=. --cov-config=.coveragerc --cov-report=html
    ```

### Файлы тестов

*   `test_backends.py`
*   `test_chatgpt.py`
*   `test_consumers.py`
*   `test_decorator.py`
*   `test_forms.py`
*   `test_models.py`
*   `test_views.py`

## 📑 Запуск Pylint

Чтобы запустить pylint, и проверить, на сколько чистый код:

* Обязательно выполните команду в виртуальном окружении:

    ```bash
    pip install -r requirements.txt
    ```

* Выполните команду

    ```bash
    pylint --load-plugins pylint_django --django-settings-module=RecruitHelper RecruitHelper/ --ignore=migrations
    ```

## 📄 Создание документации

* Обязательно выполните команду в виртуальном окружении:

    ```bash
    pip install -r requirements.txt
    ```

* Выполните команду генерации документации:

    ```bash
    sphinx-build -b html docs/source static/docs
    ```

* Готово! Ваша документация в static/docs

  При запуске локального сервера вы сможете увидеть её по ссылке:
  ```
  http://localhost:8000/docs/index.html
  ```

## 🤝 Вклад в проект

Над проектом работали:

- Стояновский Никита (TeamLead, Fullstack)
- Гусев Егор (Fullstack)
- Сыроегин Андрей (Frontend)
- Априамов Богдан (Backend)
- Васильев Матвей (Backend)
- Кирюшин Роман (Backend)
![Pylint Score](https://img.shields.io/badge/pylint-8.42-blue) 

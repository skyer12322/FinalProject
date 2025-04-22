FROM python:latest

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install -r requirements.txt

COPY . .

RUN chmod +x startup.sh

CMD ["python", "manage.py", "runserver", "0.0.0.0:10000"]
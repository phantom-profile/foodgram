FROM python:3.8.5

# Здесь можно добавлять пакеты, которые необходимы для работы приложения
RUN apt update

WORKDIR /code

# Сначала копируем requirements.txt, для того, чтобы образ собирался быстрее (см. слои докера)
COPY requirements.txt /code/
RUN pip install -r requirements.txt

# Далее копируем сам код приложения
COPY . /code/
WORKDIR /code/

EXPOSE 8000

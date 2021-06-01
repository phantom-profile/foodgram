FROM python:3.8.5
LABEL author='Phantom-profile' version=1.1

WORKDIR /code
COPY requirements.txt /code
RUN pip3 install -r requirements.txt
COPY . /code

CMD gunicorn api_yamdb.wsgi:application --bind 0.0.0.0:8000


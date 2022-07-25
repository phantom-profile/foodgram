# foodgram-project

![foodgram workflow](https://github.com/phantom-profile/foodgram/actions/workflows/foodgram_workflow.yml/badge.svg)

Used technologies: Python3, Django, DRF, Docker (docker-compose)

Project description:

_Website for people who loves tasty food and wants to share cooking knowledges with others_

how to set up site on server
1) there must be .env, docker-compose.yaml and default.conf for nginx on server in app-dir
2) Pull web-site image from docker
        
        sudo docker pull phantom8profile/foodgram:latest
3) Stop all containers if they were 
        
        sudo docker-compose stop
4) build containers from docker-compose (db, django-app (web), nginx)
    
        sudo docker-compose up -d --build
5) Make migrations from models to database
        
        sudo docker-compose exec -T web python manage.py makemigrations recipes --noinput
        
        sudo docker-compose exec -T web python manage.py makemigrations users --noinput

7) Migrate tables into database

        sudo docker-compose exec -T web python manage.py migrate --noinput
8) Collect all static files from app 
        
        sudo docker-compose exec -T web python manage.py collectstatic --no-input

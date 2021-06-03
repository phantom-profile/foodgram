# foodgram-project

![foodgram workflow](https://github.com/phantom-profile/foodgram/actions/workflows/foodgram_workflow.yml/badge.svg)

Used technologies: Python3, Django, DRF, Docker (docker-compose)

Project description:

_Website for people who loves tasty food and wants to share cooking knowledges with others_

Link to foodgtam - http://84.252.132.195/

Some endpoints 
1) Ror logged out users
        
- http://84.252.132.195/ - main page with recipes

- http://84.252.132.195/auth/signup/ - registration form

- http://84.252.132.195/profiles/admin/ - my page

- http://84.252.132.195/recipes/2/ - my first recipe

2) For logged in users

- http://84.252.132.195/recipes/create/ - recipe creation form

- http://84.252.132.195/subscriptions/ - your subscriptions

- http://84.252.132.195/favourites/ - your favorite recipes

- http://84.252.132.195/purchases/ - recipes which you probably want to cook

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

#!/bin/bash
pipenv install --dev
[ ! -f .env ] && [ -f .env.example ] && cp .env.example .env
pipenv run python manage.py migrate
pipenv run python manage.py create_test_data
echo "Запуск: pipenv run python manage.py runserver"
echo "Создать суперпользователя для django admin: pipenv run python manage.py createsuperuser"
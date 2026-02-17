.PHONY: up down build migrate makemigrations superuser seed lint format test

up:
	docker compose up --build

down:
	docker compose down

build:
	docker compose build

migrate:
	docker compose run --rm web python manage.py migrate

makemigrations:
	docker compose run --rm web python manage.py makemigrations

superuser:
	docker compose run --rm web python manage.py createsuperuser

seed:
	docker compose run --rm web python manage.py seed_demo

lint:
	ruff check .

format:
	ruff format .

test:
	pytest -q

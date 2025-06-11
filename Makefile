.PHONY: check-tools compile super install install-docker sync sync-docker mypy lint format test check migrations migrate run shell start-databases down-docker purge-databases run-docker restore ishell restore-docker

help:
	@echo 'make check-tools     - ensure pip-tools present in environment'
	@echo 'make compile         - compile requirements files'
	@echo 'make install         - install requirements/requirements.dev.txt'
	@echo 'make install-docker  - install requirements/requirements.dev.txt within docker container.'
	@echo 'make sync            - Compile and then install pip dependencies.'
	@echo 'make sync-docker     - Compile and then install pip dependencies within docker container.'
	@echo 'make super           - Creates superuser with u:test@test.com, p:test.'
	@echo 'make mypy            - runs MyPy.'
	@echo 'make lint            - runs ruff linter.'
	@echo 'make format          - runs ruff code formater.'
	@echo 'make test            - runs tests.'
	@echo 'make check           - runs tests and code quality checks. These checks should pass before pushing code'
	@echo 'make migrations      - runs django makemigrations command.'
	@echo 'make migrate         - applies django migrations.'
	@echo 'make run             - starts django server at http://localhost:8000 for local development.'
	@echo 'make shell           - starts interactive django shell.'
	@echo 'make ishell          - starts interactive django shell (all models are automatically imported).'
	@echo 'make start-databases - starts postgres in background'
	@echo 'make down-docker     - stops docker containers and removes them'
	@echo 'make purge-databases - stop postgres and purge data volume'
	@echo 'make run-docker      - starts docker containers'
	@echo 'make restore         - restores database.sql to docker-compose database'
	@echo 'make restore-docker  - restores database.sql to docker-compose database when run from django docker container'

check-tools:
	pip install pip==24.2 uv==0.4.12

compile: check-tools
	uv pip compile requirements/requirements.in -o requirements/requirements.txt
	uv pip compile requirements/requirements.dev.in -o requirements/requirements.dev.txt

super:
	export DJANGO_SUPERUSER_EMAIL=test@test.com; export DJANGO_SUPERUSER_PASSWORD=test; python manage.py createsuperuser --noinput

install: check-tools
	uv pip sync requirements/requirements.dev.txt

install-docker: check-tools
	uv pip sync requirements/requirements.dev.txt --system

sync: compile install

sync-docker: compile install-docker

mypy:
	mypy apps --config-file mypy.ini

lint:
	ruff check --fix

format:
	ruff format

test:
	pytest apps

check: format lint mypy test

migrations:
	python manage.py makemigrations

migrate:
	python manage.py migrate

run:
	python manage.py runserver 0.0.0.0:8000

shell:
	python manage.py shell

ishell:
	export DJANGO_SETTINGS_MODULE=conf.settings_test; python manage.py shell_plus --ipython

start-databases:
	docker compose -f docker-compose.yml up -d postgres

down-docker:
	docker compose -f docker-compose.yml down --remove-orphans

purge-databases: down-docker
	docker compose -f docker-compose.yml rm postgres -fv

run-docker:
	docker compose -f docker-compose.yml up -d

restore:
	export PGPASSWORD=django; cat database.sql | psql -h 127.0.0.1 -p 9432 -U django

restore-docker:
	export PGPASSWORD=django; cat database.sql | psql -h postgres -p 5432 -U django

upgrade-all-libs: check-tools
	uv pip compile requirements/requirements.in -o requirements/requirements.txt --upgrade
	uv pip compile requirements/requirements.dev.in -o requirements/requirements.dev.txt --upgrade

# demo-saltiniai

This repository is small Django service to create and expose test data that can be used for testing `spinta`. 

Test data can be created via Django admin page.

Endpoints are written using `spyne` package that can return data in different formats including:
  - JSON
  - XML
  - SOAP
  - [TBD] WSDL

## OpenAPI documentation

Documentation dynamically generated with OpenAPI3. It can be reached:

- `/schema/swagger/` for Swagger UI
- `/schema/redoc/` for ReDoc UI

## Get started
### I. Docker

For Mac users - install latest [Docker Desktop](https://docs.docker.com/desktop/mac/install/)
For non-mac install docker and docker-compose system.

Clone project and start using:

```sh
make run-docker
```

### II. Virtualenv (OSX)

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.10

/usr/local/opt/python@3.10/bin/pip3 install virtualenv
/usr/local/opt/python@3.10/bin/python3 -m virtualenv .venv

source .venv/bin/activate
make sync
```

### Wrapped commands
Project is using `make` as universal wrapper. All most common commands are packed in
```shell script
$ make help
make check-tools     - ensure pip-tools present in environment
make compile         - compile requirements files
make install         - install requirements/requirements.dev.txt
make install-docker  - install requirements/requirements.dev.txt within docker container
make sync            - Compile and then install pip depenecies
make sync-docker     - Compile and then install pip dependencies within docker container
make super           - Creates superuser with u:test@test.com, p:test
make mypy            - runs MyPy
make lint            - runs ruff linter
make format          - runs ruff code formater
make test            - runs tests
make check           - runs tests and code quality checks. These checks should pass before pushing code
make migrations      - runs django makemigrations command
make migrate         - applies django migrations
make run             - starts django server at http://localhost:8000 for local development
make shell           - starts interactive django shell
make ishell          - starts interactive django shell (all models are automatically imported)
make start-databases - starts postgres in background
make down-docker     - stops docker containers and removes them
make purge-databases - stop postgres and purge data volume
make run-docker      - starts django docker environment
make restore         - restores database.sql to docker-compose database
make restore-docker  - restores database.sql to docker-compose database when run from django docker container
```

### Environment management
#### Using make command within docker
```shell script
$ make run-docker
/app $ make mypy
mypy apps --config-file mypy.ini
Success: no issues found in 57 source files
/app $ 
```
or oneliner (useful when images needs to be build from scratch)
```shell script
echo "make mypy" | make run-docker
```

#### Restoring database
CI has ability dump development databases for local debugging/testing. For quick restore of the database to docker-compose, from active python environment run:
```shell script
make restore         - restores database.sql to docker-compose database
```
#### Starting database containers
```shell script
make start-databases - starts redis and postgres in background
```

## Project dependencies

Dependencies are storied `requirements.in, requirements.dev.in` and managed by pip-tools.

## tests locally (using Pycharm IDE)

```sh

# setup dependencies 

create venv IDE project settings -> interpreter -> show all -> add (create somewhere outside project dir)
pip install -r requirements.txt
setup database if you have skipped creating docker based one from instructions above


# setup tests

run/debug configurations -> templates -> Django tests 
-> set path to tests `Custom settings` (usually `conf/settings_test.py`) 
-> set config to DB via `Enviroment variables` field. 
Available variables are - 'DB_NAME', 'DB_USER', 'DB_HOST', 'DB_PORT'. 
If using docker database from instructions above DB_HOST=localhost;DB_PORT=9432; should be enough.
Run tests from opened test file class or method by clicking on green arrow on the left 
or whole directory/app tests by right clicking on them from IDE project view -> Run:test
```

## Production deploy (Dockerized)
### Prerequisites:
Docker
Docker-compose
Cloned repo

### Create file where secrets and other environment variables will be stored. Enable Production Run Mode
```sh
touch .env
echo "RUN_MODE=PRODUCTION" >> .env
```
Add other env variables you need like database credentials. 
Check docker-compose for predefined ones.

### Start application

Build application Docker image
```sh
docker build . -t demo-saltiniai -f production.Dockerfile
```

Launch application from image with external database connected.
```sh
docker run --env-file .env -d demo-saltiniai
```

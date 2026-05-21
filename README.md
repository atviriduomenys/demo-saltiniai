# demo-saltiniai

This repository is small Django service to create and expose test data that can be used for testing `spinta`. 

Test data can be created via Django admin page or by using [data generating endpoints](#Data generation endpoints).

Endpoints are written using [spyne](http://spyne.io/) that can return data in different formats including:
  - JSON
  - XML
  - SOAP
  - WSDL
  - [TBD] CSV
  - [TBD] XLSX

## API endpoints

### Data generation endpoints

Demo-saltiniai service allows generating test data for `spinta` project.

Each model has its own endpoint that can be used to generate test data for that model.

Available models: 

- `administration`
- `administrativeunit`
- `continent`
- `country`
- `county`
- `document`
- `eldership`
- `municipality`
- `settlement`
- `title`

To generate test data you have to access the endpoint using a `POST` request and input the quantity of instances you want to generate in `json` format. The url for the endpoint is formed as follows:

    https://test-data.data.gov.lt/api/v1/address_registry/{model}/generate/

Example using [httpie](https://httpie.io/cli), on a local development environment:

```zsh
make run-docker

TOKEN=$(http post :8000/api/v1/token/ username=test@test.com password=test | jq -r .access)
AUTH="Authorization: Token $TOKEN"
echo $AUTH

http -v post :8000/api/v1/address_registry/country/generate/ $AUTH quantity:=100
http -v post :8000/api/v1/address_registry/administration/generate/ $AUTH quantity:=100
```

Examples in raw HTTP:

```http
POST /api/v1/address_registry/country/generate/ HTTP/1.1
Authorization: Token ***
Content-Type: application/json

{
    "quantity": 100
}
```

HTTP atsakymo pavyzdys:

```http
HTTP/1.1 201 Created
Allow: POST, OPTIONS
```

## Spinta UAPI service

When you run `make docker` on you local development environment, you will get access to Spinta UAPI service running with `manifest/datasets/gov/vssa/demo/*/*.csv` manifest tables, which you can access
under:

<http://localhost:8080/datasets/gov/vssa/demo/:ns>

to test data conversion from different data sources.

## OpenAPI documentation

Documentation dynamically generated with OpenAPI3. It can be reached:

- `/swagger/` for Swagger UI (<https://test-data.data.gov.lt/swagger/>)
- `/redoc/` for ReDoc UI (<https://test-data.data.gov.lt/redoc/>)


## Data Access Endpoints

Demo-saltiniai service allows accessing the test data of certain models and in certain formats.

You can access data enpoints using following URL pattern:

    https://test-data.data.gov.lt/api/v1/{dataset}/{format}/

Where `dataset` is one of:

- `cities`
- `countries`
- `documents`
- `settlements`

And `format` is one of:

- `json`
- `xml`
- `soap`

There is also a PostgreSQBL data source available from docker compose under `saltiniai-database` host name.

### JSON Format Endpoints

<https://test-data.data.gov.lt/api/v1/>

#### REST API Endpoints

<https://test-data.data.gov.lt/api/v1/documents/>

- `https://test-data.data.gov.lt/api/v1/documents/{id}/`  
  Returns a list of documents, with each document including its associated document author.

- `https://test-data.data.gov.lt/api/v1/settlements/{id}/`  
  Returns a list of continents, with each continent containing its related countries and each country containing its related settlements.

#### JSON Service Endpoints

- <https://test-data.data.gov.lt/api/v1/cities/json/city_names>  
  Returns a list of titles, with each title including its associated settlement.

- <https://test-data.data.gov.lt/api/v1/cities/json/cities>  
  Returns a list of settlements with each settlement including a list of its associated titles.

- <https://test-data.data.gov.lt/api/v1/countries/json/continents>  
  Returns a list of continents.

- <https://test-data.data.gov.lt/api/v1/countries/json/countries>
  Returns a list of countries.

- <https://test-data.data.gov.lt/api/v1/documents/json/documents>  
  Returns a list of documents, with each document including its associated document author.

- <https://test-data.data.gov.lt/api/v1/documents/json/document_authors>
  Returns a list of document authors.

### SOAP Format Endpoints

#### WSDL Endpoints

- <https://test-data.data.gov.lt/api/v1/documents/soap/?wsdl>
- <https://test-data.data.gov.lt/api/v1/cities/soap/?wsdl>
- <https://test-data.data.gov.lt/api/v1/countries/soap/?wsdl>

Returns the WSDL for the service.

#### SOAP Service Endpoints
- <https://test-data.data.gov.lt/api/v1/cities/soap/city_names>  
  SOAP service that returns a list of titles, with each title including its associated settlement.

- <https://test-data.data.gov.lt/api/v1/cities/soap/cities>  
  SOAP service that returns a list of settlements with each settlement including a list of its associated titles.

- <https://test-data.data.gov.lt/api/v1/countries/soap/continents>  
  SOAP service that returns a list of continents.

- <https://test-data.data.gov.lt/api/v1/countries/soap/countries>  
  SOAP service that returns a list of countries.

- <https://test-data.data.gov.lt/api/v1/documents/soap/documents>  
  SOAP service that returns a list of documents, with each document including its associated document author.

- <https://test-data.data.gov.lt/api/v1/documents/soap/document_authors>  
  SOAP service that returns a list of document authors.

**Note:** All SOAP endpoints require XML POST requests with proper SOAP envelope structure.

## Review app environment

Deployments are performed with Drone CI using `docker-compose.review-apps.yml` and is avaialbe at

<https://test-data.data.gov.lt/admin/>

## Running locally

### Using Docker

For Linux install `docker` and `docker-compose` packages.

For Mac users - install latest [Docker Desktop](https://docs.docker.com/desktop/mac/install/)

Clone project and start using:

```sh
make run-docker
```

### Using Virtualenv

#### For OSX users

Install `gdal`:

```sh
brew install gdal
```

Install Python:

```sh
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python@3.10
```

Install `virtualenv` (or use any other virtual environment tool):
```sh
/usr/local/opt/python@3.10/bin/pip3 install virtualenv
/usr/local/opt/python@3.10/bin/python3 -m virtualenv .venv
```

Start services:
```sh
source .venv/bin/activate
make sync
make start-databases
make run
```

### Wrapped commands

Project is using `make` as universal wrapper. All most commonly used commands are packed in

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

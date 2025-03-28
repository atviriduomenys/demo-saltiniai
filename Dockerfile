FROM python:3.10-alpine

ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR 1
EXPOSE 8000 8000

# Add system requirements
RUN apk add --no-cache jq gettext sed bash curl docker-cli git binutils make
# Add runtime dependencies
RUN apk add --no-cache libpq libxslt libjpeg zlib jpeg postgresql-client gdal-dev proj-dev geos-dev

COPY requirements/requirements.dev.txt requirements/requirements.dev.txt
COPY Makefile Makefile

RUN apk add --no-cache --virtual build-deps gcc g++ musl-dev postgresql-dev libxslt-dev jpeg-dev libffi-dev rust cargo && make install-docker

RUN rm -rf requirements
RUN rm -f Makefile

VOLUME /app
VOLUME /static
WORKDIR /app

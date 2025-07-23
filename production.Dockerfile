ARG IMAGE=base
FROM python:3.10-alpine as base

ENV PYTHONUNBUFFERED 1
ENV PIP_NO_CACHE_DIR 1
EXPOSE 8000 8000

# Add runtime dependencies
RUN apk add --no-cache libpq libxslt libjpeg zlib jpeg bash postgresql-client binutils gdal-dev proj-dev geos-dev

COPY requirements/requirements.txt .

RUN apk add --no-cache --virtual build-deps gcc g++ musl-dev postgresql-dev libxslt-dev jpeg-dev libffi-dev git rust cargo \
	&& pip install --no-cache-dir pip-tools==7.4.1 pip==24.2 \
	&& pip-sync \
	&& apk --purge del build-deps

RUN rm -f requirements.txt

FROM $IMAGE as build

RUN mkdir /app
COPY . /app/
WORKDIR /app/
CMD ["sh", "entrypoint.sh"]

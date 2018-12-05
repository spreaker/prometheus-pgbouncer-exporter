FROM python:3.6-alpine

# Install dependencies
COPY requirements.txt /prometheus-pgbouncer-exporter/
RUN  apk add --update --no-cache postgresql-dev gcc musl-dev && \
     pip install -r /prometheus-pgbouncer-exporter/requirements.txt

WORKDIR /prometheus-pgbouncer-exporter

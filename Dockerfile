FROM python:3.6.7-alpine

RUN apk update && \
 apk add postgresql-libs && \
 apk add --virtual .build-deps gcc musl-dev postgresql-dev && \
 python3 -m pip install prometheus-pgbouncer-exporter==2.0.1 --no-cache-dir && \
 apk --purge del .build-deps

ENV PGBOUNCER_EXPORTER_HOST="127.0.0.1" \
    PGBOUNCER_EXPORTER_PORT=9127 \
    PGBOUNCER_USER="pgbouncer" \
    PGBOUNCER_PASS="" \
    PGBOUNCER_HOST="localhost" \
    PGBOUNCER_PORT=6432

EXPOSE 9127

COPY config.docker.yml /etc/pgbouncer-exporter/config.yml

ENTRYPOINT ["pgbouncer-exporter"]
CMD ["--config", "/etc/pgbouncer-exporter/config.yml"]

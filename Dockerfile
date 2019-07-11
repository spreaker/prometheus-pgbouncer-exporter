FROM python:3.6.7-alpine

ADD . /

RUN apk update
RUN apk add curl
RUN apk add nmap
RUN apk add postgresql-libs
RUN apk add --virtual .build-deps gcc musl-dev postgresql-dev
RUN python3 -m pip install . --no-cache-dir --verbose
RUN apk --purge del .build-deps

EXPOSE 9127

COPY config.docker.yml /etc/pgbouncer-exporter/config.yml

ENTRYPOINT ["pgbouncer-exporter"]
CMD ["--config", "/etc/pgbouncer-exporter/config.yml"]

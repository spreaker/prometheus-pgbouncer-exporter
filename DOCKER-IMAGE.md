This public image provides an easy way to run the [prometheus-pgbouncer-exporter](https://github.com/spreaker/prometheus-pgbouncer-exporter).


## Basic configuration via environment variables

The image is shipped with a [default config file](https://github.com/spreaker/prometheus-pgbouncer-exporter/blob/master/config.docker.yml) which should be suitable to cover a basic usage. The default config file supports the following placeholders to be replaced via environment variables:


| Environment variable    | Default value | Description |
| ----------------------- | ------------- | ----------- |
| PGBOUNCER_EXPORTER_HOST | `127.0.0.1`   | Host on which the exporter should listen to |
| PGBOUNCER_EXPORTER_PORT | `9127`        | Port on which the exporter should listen to |
| PGBOUNCER_HOST          | `localhost`   | Host of the backend pgbouncer to which the exporter should connect to |
| PGBOUNCER_PORT          | `6432`        | Port of the backend pgbouncer to which the exporter should connect to |
| PGBOUNCER_USER          | `pgbouncer`   | Username used to connect to pgbouncer |
| PGBOUNCER_PASS          | _empty_       | Password used to connect to pgbouncer |


## Providing a custom configuration file

If the default config file doesn't fit your use case, you can provide a custom one mounting it as a single-file to `/etc/pgbouncer-exporter/config.yml`.

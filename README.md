# Prometheus exporter for PgBouncer


## How to use it

You have two options to use it:

1. Manually install and run the `prometheus-pgbouncer-exporter` Python package
2. Use the [Docker image available on Docker hub](https://hub.docker.com/r/spreaker/prometheus-pgbouncer-exporter/) (_see instructions on Docker hub_)


## How to manually install and run it

The following will install the exporter whose entrypoint binary is called `pgbouncer-exporter`:

```
pip3 install prometheus-pgbouncer-exporter
```

The exporter accepts configuration via config file, you can specify with `--config` argument:

`pgbouncer-exporter --config ./config.yml`

Available arguments:

```
--config CONFIG         Path to config file
--log-level LOG_LEVEL   Minimum log level. Accepted values are: DEBUG, INFO,
                        WARNING, ERROR, CRITICAL
--log-file LOG_FILE     Path to log file or 'stdout' to log on console. Signal
                        with -HUP to re-open log file descriptor
```


## Features

- [Supports multiple pgbouncer instances](#why-supporting-multiple-pgbouncer-instances)
- Allow to configure extra labels for each pgbouncer instance
- Allow to configure timeouts on pgbouncer connections
- Allow to filter databases for which metrics are exported with `include_databases` and `exclude_databases`


### Why supporting multiple pgbouncer instances?

PgBouncer is a single thread application and so can only saturate a single CPU core on high load. In high load environments, it's common practice to run multiple pgbouncer processes per machine (one for each CPU core) and load balance traffic among them. Ideally we want to run a single exporter instance per machine, capable to monitor 1+ pgbouncer(s) running on the machine itself.


## Exported metrics

The exporter exports the following metrics for each monitored pgbouncer instance:

| Metric name                                         | Type     | PgBouncer | Description      |
| --------------------------------------------------- | -------- | --------- | ---------------- |
| `pgbouncer_stats_requests_total`                    | counter  | _<= 1.7_  | Total number of requests pooled. Could be transactions or queries, depending on pool mode. (labels: `database`) |
| `pgbouncer_stats_queries_total`                     | counter  | _>= 1.8_  | Total number of SQL queries pooled by pgbouncer (labels: `database`) |
| `pgbouncer_stats_queries_duration_microseconds`     | counter  | _all_     | Total number of microseconds spent waiting for a server to return a query response. Includes time spent waiting for an available connection. (labels: `database`) |
| `pgbouncer_stats_waiting_duration_microseconds`     | counter  | _>= 1.8_  | Total number of microseconds spent waiting for an available connection. (labels: `database`) |
| `pgbouncer_stats_received_bytes_total`              | counter  | _all_     | Total volume in bytes of network traffic received by pgbouncer (labels: `database`) |
| `pgbouncer_stats_sent_bytes_total`                  | counter  | _all_     | Total volume in bytes of network traffic sent by pgbouncer (labels: `database`) |
| `pgbouncer_stats_transactions_total`                | counter  | _>= 1.8_  | Total number of SQL transactions pooled by pgbouncer (labels: `database`) |
| `pgbouncer_stats_transactions_duration_microseconds`| counter  | _>= 1.8_  | Total number of microseconds spent in a transaction. Includes time spent waiting for an available connection. (labels: `database`) |
| `pgbouncer_pools_client_active_connections`         | gauge    | _all_     | Client connections that are linked to server connection and can process queries (labels: `database`, `user`) |
| `pgbouncer_pools_client_waiting_connections`        | gauge    | _all_     | Client connections have sent queries but have not yet got a server connection (labels: `database`, `user`) |
| `pgbouncer_pools_server_active_connections`         | gauge    | _all_     | Server connections that linked to client (labels: `database`, `user`) |
| `pgbouncer_pools_server_idle_connections`           | gauge    | _all_     | Server connections that unused and immediately usable for client queries (labels: `database`, `user`) |
| `pgbouncer_pools_server_used_connections`           | gauge    | _all_     | Server connections that have been idle more than server_check_delay, so they needs server_check_query to run on it before it can be used (labels: `database`, `user`) |
| `pgbouncer_pools_server_testing_connections`        | gauge    | _all_     | Server connections that are currently running either server_reset_query or server_check_query (labels: `database`, `user`) |
| `pgbouncer_pools_server_login_connections`          | gauge    | _all_     | Server connections currently in logging in process (labels: `database`, `user`) |
| `pgbouncer_pools_client_maxwait_seconds`            | gauge    | _all_     | How long the first (oldest) client in queue has waited, in seconds (labels: `database`, `user`) |
| `pgbouncer_databases_database_pool_size`            | gauge    | _all_     | Configured pool size limit (labels: `database`, `backend_database`) |
| `pgbouncer_databases_database_reserve_pool_size`    | gauge    | _all_     | Configured reserve limit (labels: `database`, `backend_database`) |
| `pgbouncer_databases_database_current_connections`  | gauge    | _all_     | Total number of per-database Database connections count (labels: `database`, `backend_database`) |
| `pgbouncer_databases_database_max_connections`      | gauge    | _all_     | Maximum number of allowed connections per-database (labels: `database`, `backend_database`) |
| `pgbouncer_config_max_client_conn`                  | gauge    | _all_     | Configuration of maximum number of allowed client connections |
| `pgbouncer_config_max_user_connections`             | gauge    | _all_     | Configuration of maximum number of server connections per user |


## Configuration file

The exporter read the configuration from a yaml config file with the following syntax:

```yaml
# The host on which the exporter should listen to (defaults to 127.0.0.1)
exporter_host: 0.0.0.0

# The port on which the exporter should listen to (defaults to 9100)
exporter_port: 9100

# The list of pgbouncer instances to monitor
pgbouncers:
  -
    # The pgbouncer connection string. Supports environment variables replacement
    # Ie. $(PGBOUNCER_PASS) is replaced with the content of "PGBOUNCER_PASS" environment
    #     variable if exist, or left untouched if doesn't exist
    dsn: postgresql://pgbouncer:$(PGBOUNCER_PASS)@localhost:6431/pgbouncer

    # The pgbouncer connection timeout in seconds (defaults to 5 seconds)
    connect_timeout: 5

    # Databases to report metrics for. If omitted or empty, all databases
    # will be reported.
    include_databases:

    # Databases to exclude from metrics reporting. If omitted or empty, all
    # databases matching "include_databases" will be reported.
    exclude_databases:
      - pgbouncer

    # Extra labels to add to all metrics exported for this pgbouncer
    # instance. Required if you have configured multiple pgbouncers,
    # in order to export an unique set of metrics.
    extra_labels:
      pool_id: 1

  - dsn: postgresql://pgbouncer:$(PGBOUNCER_PASS)@localhost:6432/pgbouncer
    exclude_databases:
      - pgbouncer
    extra_labels:
      pool_id: 2
```


### Environment variables replacement

The configuration file supports environment variables replacement. If you use the syntax `$(NAME)` in any setting value, it gets replaced by the content of `NAME` environment variable or left untouched if the `NAME` environment variable does not exist.


## How to contribute

Run the **development environment**:

```
docker-compose build && docker-compose run dev
```

Then inside the container:

```
# Run tests
python -m unittest

# Run exporter
python -m prometheus_pgbouncer_exporter.cli --config ./config.yml

# Run linter
pycodestyle --max-line-length=300 prometheus_pgbouncer_exporter/*.py
```


### How to publish a new version

**Release python package**:

1. Update version in `setup.py`
2. Update `CHANGELOG.md`
3. [Release new version on GitHub](https://github.com/spreaker/prometheus-pgbouncer-exporter/releases)
4. Run `python3 setup.py sdist`
5. Upload it with `twine upload dist/*`
6. Upload the files to the Github release

**Release Docker image**:

1. Update package version in `Dockerfile`
2. Build image
   ```
   docker rmi -f prometheus-pgbouncer-exporter && \
   docker build -t prometheus-pgbouncer-exporter .
   ```
3. Tag the image and push it to Docker Hub
   ```
   docker tag prometheus-pgbouncer-exporter spreaker/prometheus-pgbouncer-exporter:latest && \
   docker push spreaker/prometheus-pgbouncer-exporter:latest

   docker tag prometheus-pgbouncer-exporter spreaker/prometheus-pgbouncer-exporter:2.0.3 && \
   docker push spreaker/prometheus-pgbouncer-exporter:2.0.3
   ```


## License

This software is released under the [MIT license](LICENSE.txt).


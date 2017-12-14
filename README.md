# Prometheus exporter for PgBouncer


## How to install

The following will install the exporter whose entrypoint binary is called `pgbouncer-exporter`:

```
pip3 install prometheus-pgbouncer-exporter
```


## How to run it

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

| Metric name                                     | Type     | Description      |
| ----------------------------------------------- | -------- | ---------------- |
| `pgbouncer_stats_queries_total`                 | counter  | Total number of SQL queries pooled by pgbouncer (labels: `database`) |
| `pgbouncer_stats_queries_duration_microseconds` | counter  | Total number of microseconds spent by pgbouncer when actively connected to PostgreSQL (labels: `database`) |
| `pgbouncer_stats_received_bytes_total`          | counter  | Total volume in bytes of network traffic received by pgbouncer (labels: `database`) |
| `pgbouncer_stats_sent_bytes_total`              | counter  | Total volume in bytes of network traffic sent by pgbouncer (labels: `database`) |
| `pgbouncer_pools_client_active_connections`     | gauge    | Client connections that are linked to server connection and can process queries (labels: `database`, `user`) |
| `pgbouncer_pools_client_waiting_connections`    | gauge    | Client connections have sent queries but have not yet got a server connection (labels: `database`, `user`) |
| `pgbouncer_pools_server_active_connections`     | gauge    | Server connections that linked to client (labels: `database`, `user`) |
| `pgbouncer_pools_server_idle_connections`       | gauge    | Server connections that unused and immediately usable for client queries (labels: `database`, `user`) |
| `pgbouncer_pools_server_used_connections`       | gauge    | Server connections that have been idle more than server_check_delay, so they needs server_check_query to run on it before it can be used (labels: `database`, `user`) |
| `pgbouncer_pools_server_testing_connections`    | gauge    | Server connections that are currently running either server_reset_query or server_check_query (labels: `database`, `user`) |
| `pgbouncer_pools_server_login_connections`      | gauge    | Server connections currently in logging in process (labels: `database`, `user`) |
| `pgbouncer_pools_client_maxwait_seconds`        | gauge    | How long the first (oldest) client in queue has waited, in seconds (labels: `database`, `user`) |


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


## Contributions

### Run locally

`python3 -m prometheus_pgbouncer_exporter.cli --config ./config.yml`

### Run tests

`python3 -m unittest`

### Ensure the code is PEP 8 compliant

`pycodestyle --max-line-length=300 prometheus_pgbouncer_exporter/*.py`

### How to publish a new version

1. [Release new version on GitHub](https://github.com/spreaker/prometheus-pgbouncer-exporter/releases)
2. Update version in `setup.py`
3. Run `python3 setup.py sdist upload -r pypi`


## License

This software is released under the [MIT license](LICENSE.txt).


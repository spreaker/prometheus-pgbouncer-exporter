# Prometheus exporter for PgBouncer


## How to install

The following will install the exporter whose entrypoint binary is called `pgbouncer-exporter`:

```
pip3 install prometheus-pgbouncer-exporter
```


## How to run it

The exporter accepts configuration via config file, you can specify with `--config` argument:

`pgbouncer-exporter --config ./config.yml`


## Exported metrics

The exporter exports the following metrics for each monitored pgbouncer instance:

| Metric name                                   | Type     | Description      |
| --------------------------------------------- | -------- | ---------------- |
| pgbouncer_stats_queries_total                 | counter  | Total number of SQL queries pooled by pgbouncer (labels: `database` ) |
| pgbouncer_stats_queries_duration_microseconds | counter  | Total number of microseconds spent by pgbouncer when actively connected to PostgreSQL (labels: `database` ) |
| pgbouncer_stats_received_bytes_total          | counter  | Total volume in bytes of network traffic received by pgbouncer (labels: `database` ) |
| pgbouncer_stats_sent_bytes_total              | counter  | Total volume in bytes of network traffic sent by pgbouncer (labels: `database` ) |
| pgbouncer_pools_client_active_connections     | gauge    | Client connections that are linked to server connection and can process queries (labels: `database`, `user` ) |
| pgbouncer_pools_client_waiting_connections    | gauge    | Client connections have sent queries but have not yet got a server connection (labels: `database`, `user` ) |
| pgbouncer_pools_server_active_connections     | gauge    | Server connections that linked to client (labels: `database`, `user` ) |
| pgbouncer_pools_server_idle_connections       | gauge    | Server connections that unused and immediately usable for client queries (labels: `database`, `user` ) |
| pgbouncer_pools_server_used_connections       | gauge    | Server connections that have been idle more than server_check_delay, so they needs server_check_query to run on it before it can be used (labels: `database`, `user` ) |
| pgbouncer_pools_server_testing_connections    | gauge    | Server connections that are currently running either server_reset_query or server_check_query (labels: `database`, `user` ) |
| pgbouncer_pools_server_login_connections      | gauge    | Server connections currently in logging in process (labels: `database`, `user` ) |
| pgbouncer_pools_client_maxwait_seconds        | gauge    | How long the first (oldest) client in queue has waited, in seconds (labels: `database`, `user` ) |



## Contributions

### Ensure the code is PEP 8 compliant

`pycodestyle --max-line-length=180 prometheus_pgbouncer_exporter/*.py`


## License

This software is released under the [MIT license](LICENSE.txt).


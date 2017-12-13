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

| Metric name                                   | Type     | Default labels     | Description      |
| --------------------------------------------- | -------- | ------------------ | ---------------- |
| pgbouncer_stats_queries_total                 | counter  | `database`         | Total number of SQL queries pooled by pgbouncer |
| pgbouncer_stats_queries_duration_microseconds | counter  | `database`         | Total number of microseconds spent by pgbouncer when actively connected to PostgreSQL |
| pgbouncer_stats_received_bytes_total          | counter  | `database`         | Total volume in bytes of network traffic received by pgbouncer |
| pgbouncer_stats_sent_bytes_total              | counter  | `database`         | Total volume in bytes of network traffic sent by pgbouncer |
| pgbouncer_pools_client_active_connections     | gauge    | `database`, `user` | Client connections that are linked to server connection and can process queries |
| pgbouncer_pools_client_waiting_connections    | gauge    | `database`, `user` | Client connections have sent queries but have not yet got a server connection |
| pgbouncer_pools_server_active_connections     | gauge    | `database`, `user` | Server connections that linked to client |
| pgbouncer_pools_server_idle_connections       | gauge    | `database`, `user` | Server connections that unused and immediately usable for client queries |
| pgbouncer_pools_server_used_connections       | gauge    | `database`, `user` | Server connections that have been idle more than server_check_delay, so they needs server_check_query to run on it before it can be used |
| pgbouncer_pools_server_testing_connections    | gauge    | `database`, `user` | Server connections that are currently running either server_reset_query or server_check_query |
| pgbouncer_pools_server_login_connections      | gauge    | `database`, `user` | Server connections currently in logging in process |
| pgbouncer_pools_client_maxwait_seconds        | gauge    | `database`, `user` | How long the first (oldest) client in queue has waited, in seconds |



## Contributions

### Ensure the code is PEP 8 compliant

`pycodestyle --max-line-length=180 prometheus_pgbouncer_exporter/*.py`


## License

This software is released under the [MIT license](LICENSE.txt).


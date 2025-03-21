# Changelog

### 2.1.3 (2025-03-21)

- Upgraded dependencies
   - `psycopg2` to to 2.9.10
   - `python` to 3.8

### 2.1.2 (2021-10-08)

- Upgraded dependencies
   - `pyyaml` to 5.4.1 also changed fixed version to minimum version
     constraint.

### 2.1.1 (2020-07-14)

- Upgraded dependencies
    - `prometheus_client` to 0.8.0
    - `psycopg2` to 2.8.5
    - `python-json-logger` to 0.1.11

### 2.1.0 (2020-07-10)
- Upgraded PyYAML to 5.3.1 to fix CVE-2017-18342 among others
- [FEATURE] Reload configuration file on SIGHUP. [#21](https://github.com/spreaker/prometheus-pgbouncer-exporter/pull/21) (thanks to [Vineet Joshi](https://github.com/jvineet))
- [FEATURE] Added new metrics taken from pgbouncer configuration [#23](https://github.com/spreaker/prometheus-pgbouncer-exporter/pull/23) (thanks to [José Gabriel Duarte](https://github.com/jgduarte-stratio))
    - `pgbouncer_databases_database_max_connections`: Maximum number of allowed connections per-database (labels: `database`, `backend_database`)
    - `pgbouncer_config_max_client_conn`: Configuration of maximum number of allowed client connections
    - `pgbouncer_config_max_user_connections`: Configuration of maximum number of server connections per user

### 2.0.3 (2020-01-07)
- Changed author of the package

### 2.0.2 (2020-01-07)
- [#17](https://github.com/spreaker/prometheus-pgbouncer-exporter/pull/17) Add `maxwait_us` to the compute of `client_maxwait_seconds` metric to have a higher precission

### 2.0.1 (2018-12-11)
- [BUGFIX] Correctly mask the DSN in logs when the password is empty

### 2.0.0 (2018-12-05)
- [BREAKING CHANGE] Renamed `pgbouncer_stats_queries_total` to `pgbouncer_stats_requests_total` on pgbouncer <= 1.7
- [FEATURE] Added pgbouncer >= 1.8 support [#8](https://github.com/spreaker/prometheus-pgbouncer-exporter/pull/8) (thanks to [bitglue](https://github.com/bitglue)), including the following new metrics:
    - `pgbouncer_stats_transactions_total`
    - `pgbouncer_stats_queries_total`
    - `pgbouncer_stats_transactions_duration_microseconds`
    - `pgbouncer_stats_waiting_duration_microseconds`

### 1.0.1 (2018-08-30)
- [BUGFIX] Fixed `PGBOUNCER_EXPORTER_PORT` environment variable data type [#7](https://github.com/spreaker/prometheus-pgbouncer-exporter/pull/7)

### 1.0.0 (2018-05-04)
- [FEATURE] Added `pgbouncer_databases_database_pool_size`, `pgbouncer_databases_database_reserve_pool_size` and `pgbouncer_databases_database_current_connections` metrics [#3](https://github.com/spreaker/prometheus-pgbouncer-exporter/pull/3)
- [BUGFIX] Fixed `PyYAML` dependency declaration [#4](https://github.com/spreaker/prometheus-pgbouncer-exporter/pull/4)
- [BUGFIX] Ensure the exporter immediately exit on SIGTERM

### 0.2.1 (2018-02-23)
- [#1](https://github.com/spreaker/prometheus-pgbouncer-exporter/pull/1) - Log connection or scrape failures as errors, not debug

### 0.2.0 (2017-12-14)
- Added config file validation
- Added `--log-file` cli argument support and handle of `kill -HUP` to re-open the log file description (useful in combination with logrotate)

### 0.1.2 (2017-12-14)

- Ensure the `prometheus-pgbouncer-exporter` package is installed on Python >= 3

### 0.1.1 (2017-12-13)

- Fixed run on Python < 3.6 and >= 3.0

### 0.1.0 (2017-12-13)

- Initial version (fully working on Python 3.6)

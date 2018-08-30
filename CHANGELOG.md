# Changelog

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

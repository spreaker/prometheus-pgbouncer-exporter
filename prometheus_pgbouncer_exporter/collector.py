import psycopg2
import logging
from typing import List
from psycopg2.extras import DictCursor
from prometheus_client.core import CounterMetricFamily, GaugeMetricFamily
from .config import PgbouncerConfig


class PgbouncersMetricsCollector():
    def __init__(self, configs: List[PgbouncerConfig]):
        self.collectors = list(map(lambda config: PgbouncerMetricsCollector(config), configs))

    def collect(self):
        entries = []
        metrics = {}

        # Collect all metrics data
        for collector in self.collectors:
            entries += collector.collect()

        # Instance metrics
        for data in entries:
            name = data["name"]
            metrics[name] = metrics[name] if name in metrics else self._instanceMetric(data)
            metrics[name].add_metric(value=data["value"], labels=data["labels"].values())

        return metrics.values()

    def _instanceMetric(self, data):
        if data["type"] is "counter":
            return CounterMetricFamily(data["name"], data["help"], labels=data["labels"].keys())
        elif data["type"] is "gauge":
            return GaugeMetricFamily(data["name"], data["help"], labels=data["labels"].keys())
        else:
            raise Exception("Unsupported metric type: {type}".format(type=data['type']))


class PgbouncerMetricsCollector():
    def __init__(self, config: PgbouncerConfig):
        self.config = config

    def collect(self):
        conn = False
        metrics = []
        success = True

        try:
            # Connect to pgbouncer
            conn = self._createConnection()

            # SHOW STATS
            results = self._fetchMetrics(conn, "SHOW STATS")
            if results:
                results = self._filterMetricsByIncludeDatabases(results, self.config.getIncludeDatabases())
                results = self._filterMetricsByExcludeDatabases(results, self.config.getExcludeDatabases())
                metrics += self._exportMetrics(results, "pgbouncer_stats_", [
                    # pgbouncer < 1.8
                    {"type": "counter", "column": "total_requests",    "metric": "requests_total",                     "help": "Total number of requests pooled. Could be transactions or queries, depending on pool mode."},

                    # pgbouncer >= 1.8
                    {"type": "counter", "column": "total_xact_count",  "metric": "transactions_total",                 "help": "Total number of transactions pooled"},
                    {"type": "counter", "column": "total_query_count", "metric": "queries_total",                      "help": "Total number of queries pooled"},
                    {"type": "counter", "column": "total_xact_time",   "metric": "transactions_duration_microseconds", "help": "Total number of microseconds spent in a transaction. Includes time spent waiting for an available connection."},
                    {"type": "counter", "column": "total_wait_time",   "metric": "waiting_duration_microseconds",      "help": "Total number of microseconds spent waiting for an available connection."},

                    # all versions
                    {"type": "counter", "column": "total_query_time",  "metric": "queries_duration_microseconds",      "help": "Total number of microseconds spent waiting for a server to return a query response. Includes time spent waiting for an available connection."},
                    {"type": "counter", "column": "total_received",    "metric": "received_bytes_total",               "help": "Total volume in bytes of network traffic received by pgbouncer"},
                    {"type": "counter", "column": "total_sent",        "metric": "sent_bytes_total",                   "help": "Total volume in bytes of network traffic sent by pgbouncer"},

                ], {"database": "database"}, self.config.getExtraLabels())
            else:
                success = False

            # SHOW POOLS
            results = self._fetchMetrics(conn, "SHOW POOLS")
            if results:
                results = self._filterMetricsByIncludeDatabases(results, self.config.getIncludeDatabases())
                results = self._filterMetricsByExcludeDatabases(results, self.config.getExcludeDatabases())
                metrics += self._exportMetrics(results, "pgbouncer_pools_", [
                    {"type": "gauge", "column": "cl_active",  "metric": "client_active_connections",   "help": "Client connections that are linked to server connection and can process queries"},
                    {"type": "gauge", "column": "cl_waiting", "metric": "client_waiting_connections",  "help": "Client connections have sent queries but have not yet got a server connection"},
                    {"type": "gauge", "column": "sv_active",  "metric": "server_active_connections",   "help": "Server connections that linked to client"},
                    {"type": "gauge", "column": "sv_idle",    "metric": "server_idle_connections",     "help": "Server connections that unused and immediately usable for client queries"},
                    {"type": "gauge", "column": "sv_used",    "metric": "server_used_connections",     "help": "Server connections that have been idle more than server_check_delay, so they needs server_check_query to run on it before it can be used"},
                    {"type": "gauge", "column": "sv_tested",  "metric": "server_testing_connections",  "help": "Server connections that are currently running either server_reset_query or server_check_query"},
                    {"type": "gauge", "column": "sv_login",   "metric": "server_login_connections",    "help": "Server connections currently in logging in process"},
                    {"type": "gauge", "column": "maxwait",    "metric": "client_maxwait_seconds",      "help": "How long the first (oldest) client in queue has waited, in seconds"},
                ], {"database": "database", "user": "user"}, self.config.getExtraLabels())
            else:
                success = False

            # SHOW DATABASES
            results = self._fetchMetrics(conn, "SHOW DATABASES")
            if results:
                results = self._filterMetricsByIncludeDatabases(results, self.config.getIncludeDatabases())
                results = self._filterMetricsByExcludeDatabases(results, self.config.getExcludeDatabases())
                metrics += self._exportMetrics(results, "pgbouncer_databases_", [
                    {"type": "gauge", "column": "pool_size",           "metric": "database_pool_size",           "help": "Configured Pool Size Limit"},
                    {"type": "gauge", "column": "reserve_pool",        "metric": "database_reserve_pool_size",   "help": "Configured Reserve Limit"},
                    {"type": "gauge", "column": "current_connections", "metric": "database_current_connections", "help": "Database connection count"},
                ], {"name": "database", "database": "backend_database"}, self.config.getExtraLabels())
            else:
                success = False

        except Exception as error:
            logging.getLogger().error("Unable fetch metrics from {dsn}".format(dsn=self.config.getDsnWithMaskedPassword()), extra={"exception": str(error)})

            success = False
        finally:
            if conn:
                conn.close()

        # Add pgbouncer_up metric
        metrics.append({
            "type":   "gauge",
            "name":   "pgbouncer_up",
            "value":  1 if success else 0,
            "labels": self.config.getExtraLabels(),
            "help":   "PgBouncer is UP and the scraping of all metrics succeeded"
        })

        return metrics

    def _exportMetrics(self, results, metricPrefix, metricMappings, labelMappings, extraLabels):
        metrics = []

        for result in results:
            for mapping in metricMappings:
                # Ensure the column exists
                if not mapping["column"] in result:
                    continue

                labels = {labelName: result[columnName] for columnName, labelName in labelMappings.items()}
                labels.update(extraLabels)

                metrics.append({
                    "type":   mapping["type"],
                    "name":   metricPrefix + mapping['metric'],
                    "value":  result[mapping["column"]],
                    "labels": labels,
                    "help":   mapping["help"]
                })

        return metrics

    def _filterMetricsByIncludeDatabases(self, results, databases):
        # No filtering if empty
        if not databases:
            return results

        return list(filter(lambda item: item["database"] in databases, results))

    def _filterMetricsByExcludeDatabases(self, results, databases):
        # No filtering if empty
        if not databases:
            return results

        return list(filter(lambda item: item["database"] not in databases, results))

    def _fetchMetrics(self, conn, query):
        cursor = False

        try:
            # Open a cursor
            cursor = conn.cursor(cursor_factory=DictCursor)

            # Fetch statistics
            cursor.execute(query)

            return cursor.fetchall()
        except Exception as error:
            logging.getLogger().error("Unable run query {query} on {dsn}".format(query=query, dsn=self.config.getDsnWithMaskedPassword()), extra={"exception": str(error)})

            return False
        finally:
            if cursor:
                cursor.close()

    def _createConnection(self):
        conn = psycopg2.connect(dsn=self.config.getDsn(), connect_timeout=self.config.getConnectTimeout())
        conn.set_session(autocommit=True)

        return conn

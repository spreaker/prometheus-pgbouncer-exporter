import unittest
from unittest.mock import MagicMock
from prometheus_pgbouncer_exporter.config import *
from prometheus_pgbouncer_exporter.collector import *

#
# Helpers
#

def getMetricsByName(metrics, name):
    return list(filter(lambda item: item["name"] == name, metrics))

def fetchMetricsSuccessFromPgBouncer17Mock(conn, query):
    if query == "SHOW STATS":
        return [
            {"database": "test", "total_requests": 1, "total_query_time": 2, "total_received": 3, "total_sent": 4},
            {"database": "prod", "total_requests": 4, "total_query_time": 3, "total_received": 2, "total_sent": 1}
        ]
    elif query == "SHOW POOLS":
        return [
            {"database": "test", "user": "marco", "cl_active": 1, "cl_waiting": 2, "sv_active": 3, "sv_idle": 4, "sv_used": 5, "sv_tested": 6, "sv_login": 7, "maxwait": 8, "maxwait_us": 100000 },
            {"database": "prod", "user": "marco", "cl_active": 8, "cl_waiting": 7, "sv_active": 6, "sv_idle": 5, "sv_used": 4, "sv_tested": 3, "sv_login": 2, "maxwait": 1, "maxwait_us": 200000 }
        ]
    elif query == "SHOW DATABASES":
        return [
            {"name": "test", "database": "test", "pool_size": 50, "reserve_pool": 10, "current_connections": 30, "max_connections": 0},
            {"name": "prod", "database": "prod", "pool_size": 90, "reserve_pool": 20, "current_connections": 75, "max_connections": 5}
        ]
    elif query == "SHOW CONFIG":
        return [
            {"key": "max_client_conn",      "value": 500, "changeable": "yes"},
            {"key": "max_user_connections", "value": 0,   "changeable": "yes"}
        ]
    elif query == "SHOW CLIENTS":
        return [
            {"name": "test", "client_user": "blah", "client_database": "blah", "client_replication": "blah", "client_state": "blah", "client_addr": "blah", "client_port": "blah", "client_local_addr": "blah", "client_local_port": "blah", "client_connect_time": "blah", "client_request_time": "blah", "client_wait": "blah", "client_wait_us": "blah", "client_ptr": "blah", "client_link": "blah", "client_tls": "blah", "client_application_name": "blah", "client_prepared_statements": "blah" },
            {"name": "prod", "client_user": "blah", "client_database": "blah", "client_replication": "blah", "client_state": "blah", "client_addr": "blah", "client_port": "blah", "client_local_addr": "blah", "client_local_port": "blah", "client_connect_time": "blah", "client_request_time": "blah", "client_wait": "blah", "client_wait_us": "blah", "client_ptr": "blah", "client_link": "blah", "client_tls": "blah", "client_application_name": "blah", "client_prepared_statements": "blah" }
        ]
    else:
        return False

def fetchMetricsSuccessFromPgBouncer18Mock(conn, query):
    if query == "SHOW STATS":
        return [
            {"database": "test", "total_query_count": 1, "total_xact_count": 2, "total_xact_time": 2, "total_wait_time": 1, "total_query_time": 2, "total_received": 3, "total_sent": 4},
            {"database": "prod", "total_query_count": 4, "total_xact_count": 6, "total_xact_time": 3, "total_wait_time": 2, "total_query_time": 3, "total_received": 2, "total_sent": 1}
        ]
    elif query == "SHOW POOLS":
        return [
            {"database": "test", "user": "marco", "cl_active": 1, "cl_waiting": 2, "sv_active": 3, "sv_idle": 4, "sv_used": 5, "sv_tested": 6, "sv_login": 7, "maxwait": 8, "maxwait_us": 100000 },
            {"database": "prod", "user": "marco", "cl_active": 8, "cl_waiting": 7, "sv_active": 6, "sv_idle": 5, "sv_used": 4, "sv_tested": 3, "sv_login": 2, "maxwait": 1, "maxwait_us": 200000 }
        ]
    elif query == "SHOW DATABASES":
        return [
            {"name": "test","database": "test", "pool_size": 50, "reserve_pool": 10, "current_connections": 30, "max_connections": 0},
            {"name": "prod","database": "prod", "pool_size": 90, "reserve_pool": 20, "current_connections": 75, "max_connections": 5}
        ]
    elif query == "SHOW CONFIG":
        return [
            {"key": "max_client_conn",      "value": 500, "changeable": "yes"},
            {"key": "max_user_connections", "value": 0,   "changeable": "yes"}
        ]
    elif query == "SHOW CLIENTS":
        return [
            {"name": "test", "client_user": "blah", "client_database": "blah", "client_replication": "blah", "client_state": "blah", "client_addr": "blah", "client_port": "blah", "client_local_addr": "blah", "client_local_port": "blah", "client_connect_time": "blah", "client_request_time": "blah", "client_wait": "blah", "client_wait_us": "blah", "client_ptr": "blah", "client_link": "blah", "client_tls": "blah", "client_application_name": "blah", "client_prepared_statements": "blah" },
            {"name": "prod", "client_user": "blah", "client_database": "blah", "client_replication": "blah", "client_state": "blah", "client_addr": "blah", "client_port": "blah", "client_local_addr": "blah", "client_local_port": "blah", "client_connect_time": "blah", "client_request_time": "blah", "client_wait": "blah", "client_wait_us": "blah", "client_ptr": "blah", "client_link": "blah", "client_tls": "blah", "client_application_name": "blah", "client_prepared_statements": "blah" }
        ]
    else:
        return False

def fetchMetricsPartialFailureFromPgBouncer17Mock(conn, query):
    if query == "SHOW STATS":
        return [
            {"database": "test", "total_requests": 1, "total_query_time": 2, "total_received": 3, "total_sent": 4},
            {"database": "prod", "total_requests": 4, "total_query_time": 3, "total_received": 2, "total_sent": 1}
        ]
    elif query == "SHOW POOLS":
        raise Exception("Error while fetching metrics")
    elif query == "SHOW DATABASES":
        raise Exception("Error while fetching metrics")
    elif query == "SHOW CONFIG":
        raise Exception("Error while fetching metrics")
     elif query == "SHOW CLIENTS":
        raise Exception("Error while fetching metrics")
    else:
        return False

def fetchMetricsFailureMock(conn, query):
    raise Exception("Error while fetching metrics")

#
# Tests
#

class TestPgbouncerMetricsCollector(unittest.TestCase):

    #
    # Metric: pgbouncer_up
    #

    def testShouldExportPgbouncerUpMetricOnAllMetricsScraped(self):
        config = PgbouncerConfig({})
        collector = PgbouncerMetricsCollector(config)
        collector._createConnection = MagicMock(return_value=False)
        collector._fetchMetrics = MagicMock(side_effect=fetchMetricsSuccessFromPgBouncer17Mock)

        metrics = getMetricsByName(collector.collect(), "pgbouncer_up")

        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]["type"], "gauge")
        self.assertEqual(metrics[0]["value"], 1)
        self.assertEqual(metrics[0]["labels"], {})

    def testShouldExportPgbouncerDownMetricOnNoMetricsScraped(self):
        config = PgbouncerConfig({})
        collector = PgbouncerMetricsCollector(config)
        collector._createConnection = MagicMock(return_value=False)
        collector._fetchMetrics = MagicMock(side_effect=fetchMetricsFailureMock)

        metrics = getMetricsByName(collector.collect(), "pgbouncer_up")

        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]["type"], "gauge")
        self.assertEqual(metrics[0]["value"], 0)
        self.assertEqual(metrics[0]["labels"], {})

    def testShouldExportPgbouncerDownMetricOnMetricsPartiallyScraped(self):
        config = PgbouncerConfig({})
        collector = PgbouncerMetricsCollector(config)
        collector._createConnection = MagicMock(return_value=False)
        collector._fetchMetrics = MagicMock(side_effect=fetchMetricsPartialFailureFromPgBouncer17Mock)

        metrics = getMetricsByName(collector.collect(), "pgbouncer_up")

        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]["type"], "gauge")
        self.assertEqual(metrics[0]["value"], 0)
        self.assertEqual(metrics[0]["labels"], {})

    def testShouldComputeMaxwait(self):
        config = PgbouncerConfig({})
        collector = PgbouncerMetricsCollector(config)
        collector._createConnection = MagicMock(return_value=False)
        collector._fetchMetrics = MagicMock(side_effect=fetchMetricsSuccessFromPgBouncer17Mock)

        metrics = getMetricsByName(collector.collect(), "pgbouncer_pools_client_maxwait_seconds")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "gauge")
        self.assertAlmostEqual(metrics[0]["value"], 8.1)
        self.assertEqual(metrics[0]["labels"], {"database":"test", "user":"marco"})
        self.assertEqual(metrics[1]["type"], "gauge")
        self.assertAlmostEqual(metrics[1]["value"], 1.2)
        self.assertEqual(metrics[1]["labels"], {"database":"prod", "user":"marco"})

    def testShouldExportDatabasesMetrics(self):
        config = PgbouncerConfig({})
        collector = PgbouncerMetricsCollector(config)
        collector._createConnection = MagicMock(return_value=False)
        collector._fetchMetrics = MagicMock(side_effect=fetchMetricsSuccessFromPgBouncer17Mock)

        metrics = getMetricsByName(collector.collect(), "pgbouncer_databases_database_pool_size")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "gauge")
        self.assertEqual(metrics[0]["value"], 50)
        self.assertEqual(metrics[0]["labels"], {"backend_database":"test", "database":"test"})
        self.assertEqual(metrics[1]["type"], "gauge")
        self.assertEqual(metrics[1]["value"], 90)
        self.assertEqual(metrics[1]["labels"], {"backend_database":"prod", "database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_databases_database_reserve_pool_size")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "gauge")
        self.assertEqual(metrics[0]["value"], 10)
        self.assertEqual(metrics[0]["labels"], {"backend_database":"test", "database":"test"})
        self.assertEqual(metrics[1]["type"], "gauge")
        self.assertEqual(metrics[1]["value"], 20)
        self.assertEqual(metrics[1]["labels"], {"backend_database":"prod", "database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_databases_database_current_connections")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "gauge")
        self.assertEqual(metrics[0]["value"], 30)
        self.assertEqual(metrics[0]["labels"], {"backend_database":"test", "database":"test"})
        self.assertEqual(metrics[1]["type"], "gauge")
        self.assertEqual(metrics[1]["value"], 75)
        self.assertEqual(metrics[1]["labels"], {"backend_database":"prod", "database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_databases_database_max_connections")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "gauge")
        self.assertEqual(metrics[0]["value"], 0)
        self.assertEqual(metrics[0]["labels"], {"backend_database":"test", "database":"test"})
        self.assertEqual(metrics[1]["type"], "gauge")
        self.assertEqual(metrics[1]["value"], 5)
        self.assertEqual(metrics[1]["labels"], {"backend_database":"prod", "database":"prod"})

    def testShouldExportConfigMetrics(self):
        config = PgbouncerConfig({})
        collector = PgbouncerMetricsCollector(config)
        collector._createConnection = MagicMock(return_value=False)
        collector._fetchMetrics = MagicMock(side_effect=fetchMetricsSuccessFromPgBouncer17Mock)

        metrics = getMetricsByName(collector.collect(), "pgbouncer_config_max_client_conn")
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]["type"], "gauge")
        self.assertEqual(metrics[0]["value"], 500)

        metrics = getMetricsByName(collector.collect(), "pgbouncer_config_max_user_connections")
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]["type"], "gauge")
        self.assertEqual(metrics[0]["value"], 0)


    def testShouldExportQueriesMetricsFromPgBouncer17(self):
        config = PgbouncerConfig({})
        collector = PgbouncerMetricsCollector(config)
        collector._createConnection = MagicMock(return_value=False)
        collector._fetchMetrics = MagicMock(side_effect=fetchMetricsSuccessFromPgBouncer17Mock)

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_requests_total")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "counter")
        self.assertEqual(metrics[0]["value"], 1)
        self.assertEqual(metrics[0]["labels"], {"database":"test"})
        self.assertEqual(metrics[1]["type"], "counter")
        self.assertEqual(metrics[1]["value"], 4)
        self.assertEqual(metrics[1]["labels"], {"database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_queries_duration_microseconds")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "counter")
        self.assertEqual(metrics[0]["value"], 2)
        self.assertEqual(metrics[0]["labels"], {"database":"test"})
        self.assertEqual(metrics[1]["type"], "counter")
        self.assertEqual(metrics[1]["value"], 3)
        self.assertEqual(metrics[1]["labels"], {"database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_received_bytes_total")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "counter")
        self.assertEqual(metrics[0]["value"], 3)
        self.assertEqual(metrics[0]["labels"], {"database":"test"})
        self.assertEqual(metrics[1]["type"], "counter")
        self.assertEqual(metrics[1]["value"], 2)
        self.assertEqual(metrics[1]["labels"], {"database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_sent_bytes_total")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "counter")
        self.assertEqual(metrics[0]["value"], 4)
        self.assertEqual(metrics[0]["labels"], {"database":"test"})
        self.assertEqual(metrics[1]["type"], "counter")
        self.assertEqual(metrics[1]["value"], 1)
        self.assertEqual(metrics[1]["labels"], {"database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_queries_total")
        self.assertEqual(len(metrics), 0)

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_transactions_total")
        self.assertEqual(len(metrics), 0)

    def testShouldExportQueriesMetricsFromPgBouncer18(self):
        config = PgbouncerConfig({})
        collector = PgbouncerMetricsCollector(config)
        collector._createConnection = MagicMock(return_value=False)
        collector._fetchMetrics = MagicMock(side_effect=fetchMetricsSuccessFromPgBouncer18Mock)

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_queries_total")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "counter")
        self.assertEqual(metrics[0]["value"], 1)
        self.assertEqual(metrics[0]["labels"], {"database":"test"})
        self.assertEqual(metrics[1]["type"], "counter")
        self.assertEqual(metrics[1]["value"], 4)
        self.assertEqual(metrics[1]["labels"], {"database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_transactions_total")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "counter")
        self.assertEqual(metrics[0]["value"], 2)
        self.assertEqual(metrics[0]["labels"], {"database":"test"})
        self.assertEqual(metrics[1]["type"], "counter")
        self.assertEqual(metrics[1]["value"], 6)
        self.assertEqual(metrics[1]["labels"], {"database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_transactions_duration_microseconds")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "counter")
        self.assertEqual(metrics[0]["value"], 2)
        self.assertEqual(metrics[0]["labels"], {"database":"test"})
        self.assertEqual(metrics[1]["type"], "counter")
        self.assertEqual(metrics[1]["value"], 3)
        self.assertEqual(metrics[1]["labels"], {"database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_waiting_duration_microseconds")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "counter")
        self.assertEqual(metrics[0]["value"], 1)
        self.assertEqual(metrics[0]["labels"], {"database":"test"})
        self.assertEqual(metrics[1]["type"], "counter")
        self.assertEqual(metrics[1]["value"], 2)
        self.assertEqual(metrics[1]["labels"], {"database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_queries_duration_microseconds")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "counter")
        self.assertEqual(metrics[0]["value"], 2)
        self.assertEqual(metrics[0]["labels"], {"database":"test"})
        self.assertEqual(metrics[1]["type"], "counter")
        self.assertEqual(metrics[1]["value"], 3)
        self.assertEqual(metrics[1]["labels"], {"database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_received_bytes_total")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "counter")
        self.assertEqual(metrics[0]["value"], 3)
        self.assertEqual(metrics[0]["labels"], {"database":"test"})
        self.assertEqual(metrics[1]["type"], "counter")
        self.assertEqual(metrics[1]["value"], 2)
        self.assertEqual(metrics[1]["labels"], {"database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_sent_bytes_total")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "counter")
        self.assertEqual(metrics[0]["value"], 4)
        self.assertEqual(metrics[0]["labels"], {"database":"test"})
        self.assertEqual(metrics[1]["type"], "counter")
        self.assertEqual(metrics[1]["value"], 1)
        self.assertEqual(metrics[1]["labels"], {"database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_requests_total")
        self.assertEqual(len(metrics), 0)

    #
    # Databases filtering
    #

    def testShouldNotFilterDatabasesByDefault(self):
        config = PgbouncerConfig({})
        collector = PgbouncerMetricsCollector(config)
        collector._createConnection = MagicMock(return_value=False)
        collector._fetchMetrics = MagicMock(side_effect=fetchMetricsSuccessFromPgBouncer17Mock)

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_requests_total")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "counter")
        self.assertEqual(metrics[0]["value"], 1)
        self.assertEqual(metrics[0]["labels"], {"database":"test"})
        self.assertEqual(metrics[1]["type"], "counter")
        self.assertEqual(metrics[1]["value"], 4)
        self.assertEqual(metrics[1]["labels"], {"database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_pools_client_active_connections")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "gauge")
        self.assertEqual(metrics[0]["value"], 1)
        self.assertEqual(metrics[0]["labels"], {"database":"test", "user": "marco"})
        self.assertEqual(metrics[1]["type"], "gauge")
        self.assertEqual(metrics[1]["value"], 8)
        self.assertEqual(metrics[1]["labels"], {"database":"prod", "user": "marco"})

    def testShouldNotFilterDatabasesOnEmptyIncludeDatabasesConfigOption(self):
        config = PgbouncerConfig({"include_databases":[]})
        collector = PgbouncerMetricsCollector(config)
        collector._createConnection = MagicMock(return_value=False)
        collector._fetchMetrics = MagicMock(side_effect=fetchMetricsSuccessFromPgBouncer17Mock)

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_requests_total")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "counter")
        self.assertEqual(metrics[0]["value"], 1)
        self.assertEqual(metrics[0]["labels"], {"database":"test"})
        self.assertEqual(metrics[1]["type"], "counter")
        self.assertEqual(metrics[1]["value"], 4)
        self.assertEqual(metrics[1]["labels"], {"database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_pools_client_active_connections")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "gauge")
        self.assertEqual(metrics[0]["value"], 1)
        self.assertEqual(metrics[0]["labels"], {"database":"test", "user": "marco"})
        self.assertEqual(metrics[1]["type"], "gauge")
        self.assertEqual(metrics[1]["value"], 8)
        self.assertEqual(metrics[1]["labels"], {"database":"prod", "user": "marco"})

    def testShouldFilterDatabasesByIncludeDatabasesConfigOption(self):
        config = PgbouncerConfig({"include_databases": ["prod"]})
        collector = PgbouncerMetricsCollector(config)
        collector._createConnection = MagicMock(return_value=False)
        collector._fetchMetrics = MagicMock(side_effect=fetchMetricsSuccessFromPgBouncer17Mock)

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_requests_total")
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]["type"], "counter")
        self.assertEqual(metrics[0]["value"], 4)
        self.assertEqual(metrics[0]["labels"], {"database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_pools_client_active_connections")
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]["type"], "gauge")
        self.assertEqual(metrics[0]["value"], 8)
        self.assertEqual(metrics[0]["labels"], {"database":"prod", "user": "marco"})

    def testShouldFilterDatabasesByExcludeDatabasesConfigOption(self):
        config = PgbouncerConfig({"exclude_databases": ["prod"]})
        collector = PgbouncerMetricsCollector(config)
        collector._createConnection = MagicMock(return_value=False)
        collector._fetchMetrics = MagicMock(side_effect=fetchMetricsSuccessFromPgBouncer17Mock)

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_requests_total")
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]["type"], "counter")
        self.assertEqual(metrics[0]["value"], 1)
        self.assertEqual(metrics[0]["labels"], {"database":"test"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_pools_client_active_connections")
        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]["type"], "gauge")
        self.assertEqual(metrics[0]["value"], 1)
        self.assertEqual(metrics[0]["labels"], {"database":"test", "user": "marco"})

    #
    # Metrics exported on partial failure
    #

    def testShouldReturnScrapedMetricsOnPartialFailure(self):
        config = PgbouncerConfig({})
        collector = PgbouncerMetricsCollector(config)
        collector._createConnection = MagicMock(return_value=False)
        collector._fetchMetrics = MagicMock(side_effect=fetchMetricsPartialFailureFromPgBouncer17Mock)

        metrics = getMetricsByName(collector.collect(), "pgbouncer_stats_requests_total")
        self.assertEqual(len(metrics), 2)
        self.assertEqual(metrics[0]["type"], "counter")
        self.assertEqual(metrics[0]["value"], 1)
        self.assertEqual(metrics[0]["labels"], {"database":"test"})
        self.assertEqual(metrics[1]["type"], "counter")
        self.assertEqual(metrics[1]["value"], 4)
        self.assertEqual(metrics[1]["labels"], {"database":"prod"})

        metrics = getMetricsByName(collector.collect(), "pgbouncer_pools_client_active_connections")
        self.assertEqual(len(metrics), 0)


if __name__ == '__main__':
    unittest.main()

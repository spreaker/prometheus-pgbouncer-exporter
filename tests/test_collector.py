import unittest
from unittest.mock import MagicMock
from prometheus_pgbouncer_exporter.config import *
from prometheus_pgbouncer_exporter.collector import *

#
# Helpers
#

def getMetricsByName(metrics, name):
    return list(filter(lambda item: item["name"] == name, metrics))

def fetchMetricsSuccessMock(conn, query):
    if query == "SHOW STATS":
        return [{"database": "test", "total_requests": 1, "total_query_time": 2, "total_received": 3, "total_sent": 4}]
    elif query == "SHOW POOLS":
        return [{"database": "test", "user": "marco", "cl_active": 1, "cl_waiting": 2, "sv_active": 3, "sv_idle": 4, "sv_used": 5, "sv_tested": 6, "sv_login": 7, "maxwait": 8 }]
    else:
        return False

def fetchMetricsFailureMock(conn, query):
    raise Exception("Error while fetching metrics")

def fetchMetricsPartialFailureMock(conn, query):
    if query == "SHOW STATS":
        return [{"database": "test", "total_requests": 1, "total_query_time": 2, "total_received": 3, "total_sent": 4}]
    elif query == "SHOW POOLS":
        raise Exception("Error while fetching metrics")
    else:
        return False

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
        collector._fetchMetrics = MagicMock(side_effect=fetchMetricsSuccessMock)

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
        collector._fetchMetrics = MagicMock(side_effect=fetchMetricsPartialFailureMock)

        metrics = getMetricsByName(collector.collect(), "pgbouncer_up")

        self.assertEqual(len(metrics), 1)
        self.assertEqual(metrics[0]["type"], "gauge")
        self.assertEqual(metrics[0]["value"], 0)
        self.assertEqual(metrics[0]["labels"], {})


if __name__ == '__main__':
    unittest.main()

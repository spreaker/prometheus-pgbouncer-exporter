import unittest
import os
from prometheus_pgbouncer_exporter.config import *

CURR_DIR=os.path.dirname(os.path.realpath(__file__))

class TestConfig(unittest.TestCase):


    def testShouldRaiseErrorOnUnexistingFile(self):
        config = Config()

        with self.assertRaises(Exception):
            config.read("/path/to/none.yml")

    def testShouldSupportAnEmptyConfigFile(self):
        config = Config()
        config.read(f"{CURR_DIR}/fixtures/config-empty.yml")

        self.assertEqual(config.getExporterHost(), "127.0.0.1")
        self.assertEqual(config.getExporterPort(), 9100)
        self.assertEqual(config.getPgbouncers(), [])

    def testShouldParseConfigFileWithOnePgbouncer(self):
        config = Config()
        config.read(f"{CURR_DIR}/fixtures/config-with-one-pgbouncer.yml")

        self.assertEqual(config.getExporterHost(), "0.0.0.0")
        self.assertEqual(config.getExporterPort(), 1234)
        self.assertEqual(len(config.getPgbouncers()), 1)

        self.assertEqual(config.getPgbouncers()[0].getDsn(), "postgresql://user:password@host:6431/pgbouncer")
        self.assertEqual(config.getPgbouncers()[0].getConnectTimeout(), 2)
        self.assertEqual(config.getPgbouncers()[0].getIncludeDatabases(), ["one", "two"])
        self.assertEqual(config.getPgbouncers()[0].getExcludeDatabases(), ["three"])
        self.assertEqual(config.getPgbouncers()[0].getExtraLabels(), {"first": "1", "second": "2"})


if __name__ == '__main__':
    unittest.main()

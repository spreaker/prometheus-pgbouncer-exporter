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
        self.assertEqual(config.getPgbouncers()[0].getDsnWithMaskedPassword(), "postgresql://user:***@host:6431/pgbouncer")
        self.assertEqual(config.getPgbouncers()[0].getConnectTimeout(), 2)
        self.assertEqual(config.getPgbouncers()[0].getIncludeDatabases(), ["one", "two"])
        self.assertEqual(config.getPgbouncers()[0].getExcludeDatabases(), ["three"])
        self.assertEqual(config.getPgbouncers()[0].getExtraLabels(), {"first": "1", "second": "2"})

    def testShouldParseConfigFileWithTwoPgbouncer(self):
        config = Config()
        config.read(f"{CURR_DIR}/fixtures/config-with-two-pgbouncer.yml")

        self.assertEqual(config.getExporterHost(), "0.0.0.0")
        self.assertEqual(config.getExporterPort(), 1234)
        self.assertEqual(len(config.getPgbouncers()), 2)

        self.assertEqual(config.getPgbouncers()[0].getDsn(), "postgresql://user:password@host:6431/pgbouncer")
        self.assertEqual(config.getPgbouncers()[0].getDsnWithMaskedPassword(), "postgresql://user:***@host:6431/pgbouncer")
        self.assertEqual(config.getPgbouncers()[0].getConnectTimeout(), 2)
        self.assertEqual(config.getPgbouncers()[0].getIncludeDatabases(), ["one", "two"])
        self.assertEqual(config.getPgbouncers()[0].getExcludeDatabases(), ["three"])
        self.assertEqual(config.getPgbouncers()[0].getExtraLabels(), {"first": "1", "second": "2"})

        self.assertEqual(config.getPgbouncers()[1].getDsn(), "postgresql://user:password@host:6432/pgbouncer")
        self.assertEqual(config.getPgbouncers()[1].getDsnWithMaskedPassword(), "postgresql://user:***@host:6432/pgbouncer")
        self.assertEqual(config.getPgbouncers()[1].getConnectTimeout(), 5)
        self.assertEqual(config.getPgbouncers()[1].getIncludeDatabases(), [])
        self.assertEqual(config.getPgbouncers()[1].getExcludeDatabases(), [])
        self.assertEqual(config.getPgbouncers()[1].getExtraLabels(), {})

    def testShouldInjectEnvironmentVariablesOnParsing(self):
        os.environ["TEST_USERNAME"] = "marco"
        os.environ["TEST_PASSWORD"] = "secret"
        os.environ["TEST_INCLUDE_DATABASE"] = "production"
        os.environ["TEST_EXTRA_LABEL_NAME"] = "cluster"
        os.environ["TEST_EXTRA_LABEL_VALUE"] = "users-1-1000"

        config = Config()
        config.read(f"{CURR_DIR}/fixtures/config-with-env-vars.yml")

        self.assertEqual(len(config.getPgbouncers()), 1)
        self.assertEqual(config.getPgbouncers()[0].getDsn(), "postgresql://marco:secret@host:6431/pgbouncer")
        self.assertEqual(config.getPgbouncers()[0].getIncludeDatabases(), ["production"])
        self.assertEqual(config.getPgbouncers()[0].getExtraLabels(), {"cluster": "users-1-1000"})

    def testShouldInjectEnvironmentVariablesOnParsingEvenIfEmpty(self):
        os.environ["TEST_USERNAME"] = "marco"
        os.environ["TEST_PASSWORD"] = ""
        os.environ["TEST_INCLUDE_DATABASE"] = "production"
        os.environ["TEST_EXTRA_LABEL_NAME"] = "cluster"
        os.environ["TEST_EXTRA_LABEL_VALUE"] = "users-1-1000"

        config = Config()
        config.read(f"{CURR_DIR}/fixtures/config-with-env-vars.yml")

        self.assertEqual(len(config.getPgbouncers()), 1)
        self.assertEqual(config.getPgbouncers()[0].getDsn(), "postgresql://marco:@host:6431/pgbouncer")

    def testShouldKeepOriginalConfigOnMissingEnvironmentVariables(self):
        del os.environ["TEST_USERNAME"]
        os.environ["TEST_PASSWORD"] = "secret"
        del os.environ["TEST_INCLUDE_DATABASE"]
        os.environ["TEST_EXTRA_LABEL_NAME"] = "cluster"
        os.environ["TEST_EXTRA_LABEL_VALUE"] = "users-1-1000"

        config = Config()
        config.read(f"{CURR_DIR}/fixtures/config-with-env-vars.yml")

        self.assertEqual(len(config.getPgbouncers()), 1)
        self.assertEqual(config.getPgbouncers()[0].getDsn(), "postgresql://$(TEST_USERNAME):secret@host:6431/pgbouncer")
        self.assertEqual(config.getPgbouncers()[0].getIncludeDatabases(), ["$(TEST_INCLUDE_DATABASE)"])
        self.assertEqual(config.getPgbouncers()[0].getExtraLabels(), {"cluster": "users-1-1000"})


if __name__ == '__main__':
    unittest.main()

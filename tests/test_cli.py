import unittest
import os
import signal
import threading
import time

from prometheus_pgbouncer_exporter import cli
from unittest import mock


CURR_DIR=os.path.dirname(os.path.realpath(__file__))


class TestCLI(unittest.TestCase):

    @mock.patch('prometheus_pgbouncer_exporter.cli.logging')
    def testReadConfigFile(self, mock_logging):
        mock_logger = mock.MagicMock()
        mock_logging.getLogger.return_value = mock_logger

        # should read and validate this config file without any issues
        config = cli.read_config_file(CURR_DIR + '/fixtures/config-with-one-pgbouncer.yml')

        self.assertEqual(mock_logger.info.call_count, 1)
        self.assertEqual(config.getExporterHost(), "0.0.0.0")
        self.assertEqual(config.getExporterPort(), 1234)
        self.assertEqual(len(config.getPgbouncers()), 1)

        self.assertEqual(config.getPgbouncers()[0].getDsn(), "postgresql://user:password@host:6431/pgbouncer")
        self.assertEqual(config.getPgbouncers()[0].getDsnWithMaskedPassword(), "postgresql://user:***@host:6431/pgbouncer")
        self.assertEqual(config.getPgbouncers()[0].getConnectTimeout(), 2)
        self.assertEqual(config.getPgbouncers()[0].getIncludeDatabases(), ["one", "two"])
        self.assertEqual(config.getPgbouncers()[0].getExcludeDatabases(), ["three"])
        self.assertEqual(config.getPgbouncers()[0].getExtraLabels(), {"first": "1", "second": "2"})

        # Should raise exception saying 'Cannot read config file'
        with self.assertRaises(Exception) as err:
            cli.read_config_file(CURR_DIR + '/path/to/none.yml')

        self.assertEqual('Cannot read config file', str(err.exception))
        self.assertEqual(mock_logger.fatal.call_count, 1)

        # Should raise exception saying 'Invalid config file'
        with self.assertRaises(Exception) as err:
            cli.read_config_file(CURR_DIR + '/fixtures/config-empty.yml')

        self.assertEqual('Invalid config file', str(err.exception))
        self.assertEqual(mock_logger.fatal.call_count, 2)

    @mock.patch('prometheus_pgbouncer_exporter.cli.os._exit')
    @mock.patch('prometheus_pgbouncer_exporter.collector.PgbouncersMetricsCollector.update')
    @mock.patch('prometheus_pgbouncer_exporter.collector.PgbouncersMetricsCollector.collect')
    @mock.patch('prometheus_pgbouncer_exporter.cli.argparse.ArgumentParser')
    def testSignalHandling(self, mock_argparser, mock_collect, mock_update, mock_exit):
        pid = os.getpid()
        hup_count = 0

        def send_signal():
            nonlocal hup_count
            # Keep sending HUP until PgbouncersMetricsCollector.update is called at least twice.
            # The first call is made when PgbouncersMetricsCollector class is initialized
            # Any subsequent call happens as a result of config reload from HUP
            while mock_update.call_count < 2:
                os.kill(pid, signal.SIGHUP)
                time.sleep(0.5)
                hup_count += 1
            os.kill(pid, signal.SIGTERM)

        # initialize siguhup handler to ignore sighup, this will be overridden by cli.main
        def _on_sighup(signal, frame):
            pass

        signal.signal(signal.SIGHUP, _on_sighup)

        args = mock.MagicMock()
        args.config = CURR_DIR + '/fixtures/config-with-one-pgbouncer.yml'
        args.log_file = 'stdout'
        args.log_level = 'CRITICAL'

        parser = mock.MagicMock()
        parser.parse_args.return_value = args
        mock_argparser.return_value = parser

        thread = threading.Thread(target=send_signal)
        thread.daemon = True
        thread.start()

        self.assertEqual(mock_update.call_count, 0)
        cli.main()
        self.assertEqual(mock_update.call_count, 2)
        mock_exit.assert_called_once_with(0)

        # test if hup handler aggregates hup counts and 'update' is not called on every HUP
        self.assertGreater(hup_count, mock_update.call_count)


if __name__ == '__main__':
    unittest.main()

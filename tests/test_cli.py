import unittest
import os
import signal
import threading
import time

from prometheus_pgbouncer_exporter import cli
from unittest import mock


CURR_DIR=os.path.dirname(os.path.realpath(__file__))


class TestCLI(unittest.TestCase):

    def testReadConfigFile(self):

        # should read and validate this config file without any issues
        config = cli.read_config_file(CURR_DIR + '/fixtures/config-with-one-pgbouncer.yml')

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

        # Should raise exception saying 'Invalid config file'
        with self.assertRaises(Exception) as err:
            cli.read_config_file(CURR_DIR + '/fixtures/config-empty.yml')

        self.assertEqual('Invalid config file', str(err.exception))

    @mock.patch('prometheus_pgbouncer_exporter.cli.os._exit')
    @mock.patch('prometheus_pgbouncer_exporter.collector.PgbouncersMetricsCollector.update')
    @mock.patch('prometheus_pgbouncer_exporter.collector.PgbouncersMetricsCollector.collect')
    @mock.patch('prometheus_pgbouncer_exporter.cli.argparse.ArgumentParser')
    def testSignalHandling(self, _argparser, _collect, _update, _exit):
        pid = os.getpid()
        hup_count = 0

        def send_signal():
            nonlocal hup_count
            # Keep sending HUP until PgbouncersMetricsCollector.update to be called at least twice.
            # The first call is made when PgbouncersMetricsCollector class is initialized
            # Any subsequent call happens as a result of config reload from HUP
            while _update.call_count < 2:
                os.kill(pid, signal.SIGHUP)
                time.sleep(0.5)
                hup_count += 1
            os.kill(pid, signal.SIGTERM)

        # initialize siguhup handler to ignore sighup, this will be overridden by cli.main
        def _on_sighup(signal, frame):
            pass

        signal.signal(signal.SIGHUP, _on_sighup)

        # mock argparse
        _args = mock.MagicMock()
        _args.config = CURR_DIR + '/fixtures/config-with-one-pgbouncer.yml'
        _args.log_file = 'stdout'
        _args.log_level = 'INFO'

        _parser = mock.MagicMock()
        _parser.parse_args.return_value = _args
        _argparser.return_value = _parser

        thread = threading.Thread(target=send_signal)
        thread.daemon = True
        thread.start()

        self.assertEqual(_update.call_count, 0)

        # start main service
        cli.main()

        self.assertEqual(_update.call_count, 2)

        # test if hup handler aggregates hup counts and 'update' is not called on every HUP
        self.assertGreater(hup_count, _update.call_count)

        # check if exit is gracefully called after sigterm
        _exit.assert_called_once_with(0)


if __name__ == '__main__':
    unittest.main()

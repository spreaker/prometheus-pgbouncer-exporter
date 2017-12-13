import logging
import sys
import signal
import time
import argparse
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
from pythonjsonlogger import jsonlogger
from .config import Config
from .collector import PgbouncersMetricsCollector


class SignalHandler():
    def __init__(self):
        self.shutdown = False

        # Register signal handler
        signal.signal(signal.SIGINT, self._on_signal_received)
        signal.signal(signal.SIGTERM, self._on_signal_received)

    def is_shutting_down(self):
        return self.shutdown

    def _on_signal_received(self, signal, frame):
        logging.getLogger().info("Exporter is shutting down")
        self.shutdown = True


def main():
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",     help="Path to config file", default="config.yml")
    parser.add_argument("--log-level",  help="Minimum log level. Accepted values are: DEBUG, INFO, WARNING, ERROR, CRITICAL", default="INFO")
    args = parser.parse_args()

    # Register signal handler
    signal_handler = SignalHandler()

    # Init logger
    logHandler = logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter("(asctime) (levelname) (message)", datefmt="%Y-%m-%d %H:%M:%S")
    logHandler.setFormatter(formatter)
    logging.getLogger().addHandler(logHandler)
    logging.getLogger().setLevel(args.log_level)
    logging.getLogger().info("Exporter is starting up")

    # Read config file
    config = Config()
    try:
        config.read(args.config)
        logging.getLogger().info(f"Config file successfully read from {args.config}")
    except Exception as error:
        logging.getLogger().fatal(f"Unable to read config file from {args.config}", extra={"exception": str(error)})
        sys.exit(1)

    # Register our custom collector
    REGISTRY.register(PgbouncersMetricsCollector(config.getPgbouncers()))

    # Start server
    start_http_server(config.getExporterPort(), config.getExporterHost())
    logging.getLogger().info(f"Exporter listening on {config.getExporterHost()}:{config.getExporterPort()}")

    while not signal_handler.is_shutting_down():
        time.sleep(1)

    logging.getLogger().info("Exporter has shutdown")


if __name__ == '__main__':
    main()

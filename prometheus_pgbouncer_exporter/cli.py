import logging
import sys
import signal
import time
import argparse
import os
from prometheus_client import start_http_server
from prometheus_client.core import REGISTRY
from pythonjsonlogger import jsonlogger
from .config import Config
from .collector import PgbouncersMetricsCollector


def main():
    shutdown = False

    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",     help="Path to config file", default="config.yml")
    parser.add_argument("--log-level",  help="Minimum log level. Accepted values are: DEBUG, INFO, WARNING, ERROR, CRITICAL", default="INFO")
    parser.add_argument("--log-file",   help="Path to log file or 'stdout' to log on console. Signal with -HUP to re-open log file descriptor", default="stdout")
    args = parser.parse_args()

    # Init logger
    logHandler = logging.FileHandler(args.log_file) if args.log_file is not "stdout" else logging.StreamHandler()
    formatter = jsonlogger.JsonFormatter("(asctime) (levelname) (message)", datefmt="%Y-%m-%d %H:%M:%S")
    logHandler.setFormatter(formatter)
    logging.getLogger().addHandler(logHandler)
    logging.getLogger().setLevel(args.log_level)
    logging.getLogger().info("Exporter is starting up")

    # Register signal handler
    def _on_sighup(signal, frame):
        if args.log_file is not "stdout":
            logging.getLogger().info("Received SIGHUP - log file is closing")
            logHandler.close()
            logging.getLogger().info("Received SIGHUP - log file has been re-opened")

    def _on_sigterm(signal, frame):
        logging.getLogger().info("Exporter is shutting down")
        nonlocal shutdown
        shutdown = True

    signal.signal(signal.SIGHUP, _on_sighup)
    signal.signal(signal.SIGINT, _on_sigterm)
    signal.signal(signal.SIGTERM, _on_sigterm)

    # Read config file
    config = Config()
    try:
        config.read(args.config)
        logging.getLogger().info("Config file successfully read from {file}".format(file=args.config))
    except Exception as error:
        logging.getLogger().fatal("Unable to read config file from {file}".format(file=args.config), extra={"exception": str(error)})
        sys.exit(1)

    # Validate config
    try:
        config.validate()
    except Exception as error:
        logging.getLogger().fatal("The config file {file} is invalid: {error}".format(file=args.config, error=str(error)))
        sys.exit(1)

    # Register our custom collector
    REGISTRY.register(PgbouncersMetricsCollector(config.getPgbouncers()))

    # Start server
    start_http_server(config.getExporterPort(), config.getExporterHost())
    logging.getLogger().info("Exporter listening on {host}:{port}".format(host=config.getExporterHost(), port=config.getExporterPort()))

    while not shutdown:
        time.sleep(1)

    logging.getLogger().info("Exporter has shutdown")

    os._exit(0)


if __name__ == '__main__':
    main()

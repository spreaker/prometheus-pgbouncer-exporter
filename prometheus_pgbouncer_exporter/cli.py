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


def read_config_file(config_file):
    # Read config file
    config = Config()
    try:
        config.read(config_file)
        logging.getLogger().info("Config file successfully read from {file}".format(file=config_file))
    except Exception as error:
        logging.getLogger().fatal("Unable to read config file from {file}".format(file=config_file), extra={"exception": str(error)})
        raise Exception('Cannot read config file')

    # Validate config
    try:
        config.validate()
    except Exception as error:
        logging.getLogger().fatal("The config file {file} is invalid: {error}".format(file=config_file, error=str(error)))
        raise Exception('Invalid config file')

    return config


def main():
    shutdown = False
    sighup_received_count = 0

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
        # we want to do minimum work in the signal handling for HUP, so that a HUP received
        # while handling another HUP won't change the execution order of the two HUPs
        # (second and then the first) and leave us in a broken state.
        nonlocal sighup_received_count
        sighup_received_count += 1
        logging.getLogger().info("Received SIGHUP - Incrementing HUP counter to %s",
                                 sighup_received_count)
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
    config = read_config_file(args.config)

    # Register our custom collector
    pgbcollector = PgbouncersMetricsCollector(config.getPgbouncers())
    REGISTRY.register(pgbcollector)

    # Start server
    start_http_server(config.getExporterPort(), config.getExporterHost())
    logging.getLogger().info("Exporter listening on {host}:{port}".format(host=config.getExporterHost(), port=config.getExporterPort()))

    while not shutdown:
        # check if HUPs were received in the last cycle and subsequently reload the pgbouncer hosts
        if sighup_received_count:
            logging.getLogger().info("Processing SIGHUP - Reloading pgbouncer hosts")
            sighup_received_count = 0
            config = read_config_file(args.config)
            pgbcollector.update(config.getPgbouncers())
        time.sleep(4)

    logging.getLogger().info("Exporter has shutdown")

    os._exit(0)


if __name__ == '__main__':
    main()

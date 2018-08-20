import yaml
import os
import re

# Define the regex used to replace $(ENV_VAR) with ENV_VAR value
ENV_VAR_MATCHER_PATTERN = re.compile(r'^(.*)\$\(([^\)]+)\)(.*)$')
ENV_VAR_REPLACER_PATTERN = re.compile(r'\$\(([^\)]+)\)')

# Define the regex used to mask the password in the DSN
DSN_PASSWORD_MASK_PATTERN = re.compile(r'^(.*:)([^@]+)(@.*)$')


class Config():
    def __init__(self, config={}):
        self.config = config
        self.pgbouncers = False

    def getExporterHost(self):
        return self.config["exporter_host"] if "exporter_host" in self.config else "127.0.0.1"

    def getExporterPort(self):
        return int(self.config["exporter_port"]) if "exporter_port" in self.config else 9100

    def getPgbouncers(self):
        # Lazy instance pgbouncer config
        if self.pgbouncers is False:
            if "pgbouncers" in self.config:
                self.pgbouncers = list(map(lambda item: PgbouncerConfig(item), self.config["pgbouncers"]))
            else:
                self.pgbouncers = []

        return self.pgbouncers

    def read(self, filepath):
        stream = False

        # Setup environment variables replacement
        def env_var_single_replace(match):
            return os.environ[match.group(1)] if match.group(1) in os.environ else match.group()

        def env_var_multi_replacer(loader, node):
            value = loader.construct_scalar(node)

            return re.sub(ENV_VAR_REPLACER_PATTERN, env_var_single_replace, value)

        yaml.add_implicit_resolver("!envvarreplacer", ENV_VAR_MATCHER_PATTERN)
        yaml.add_constructor('!envvarreplacer', env_var_multi_replacer)

        # Read file
        try:
            stream = open(filepath, "r")
            self.config = yaml.load(stream)

            # Handle an empty configuration file
            if not self.config:
                self.config = {}
        finally:
            if stream:
                stream.close()

    def validate(self):
        """
        Validate the configuration. Throws an exception with the error message in case
        of invalid config, or just pass on success.
        """

        # Ensure there's at least 1 pgbouncer configured
        if len(self.getPgbouncers()) == 0:
            raise Exception("There is no pgbouncer instance configured. At least 1 pgbouncer instance is required to have something to monitor.")

        # Validate all pgbouncers config
        for pgbouncerConfig in self.getPgbouncers():
            pgbouncerConfig.validate()

        # Ensure all pgbouncers extra labels are unique, on multiple pgbouncers
        if len(self.getPgbouncers()) > 1:
            labels = list(map(lambda item: item.getExtraLabels(), self.getPgbouncers()))
            duplicates = list(filter(lambda item: labels.count(item) > 1, labels))

            if duplicates or not labels:
                raise Exception("The extra_labels configured for each pgbouncer must be unique otherwise the exporter will export the same metric 2+ times with the same set of labels and then Prometheus will not ingest all metrics")


class PgbouncerConfig():
    def __init__(self, config):
        self.config = config
        self.labels = False

    def getDsn(self):
        return self.config["dsn"] if "dsn" in self.config else "postgresql://pgbouncer:@localhost:6431/pgbouncer"

    def getDsnWithMaskedPassword(self):
        match = DSN_PASSWORD_MASK_PATTERN.match(self.getDsn())
        if match:
            return match.group(1) + "***" + match.group(3)
        else:
            return self.getDsn()

    def getConnectTimeout(self):
        return self.config["connect_timeout"] if "connect_timeout" in self.config else 5

    def getIncludeDatabases(self):
        return self.config["include_databases"] if "include_databases" in self.config else []

    def getExcludeDatabases(self):
        return self.config["exclude_databases"] if "exclude_databases" in self.config else []

    def getExtraLabels(self):
        # Lazy instance extra labels
        if self.labels is False:
            if "extra_labels" in self.config:
                self.labels = {key: str(value) for key, value in self.config["extra_labels"].items()}
            else:
                self.labels = {}

        return self.labels

    def validate(self):
        """
        Validate the configuration. Throws an exception with the error message in case
        of invalid config, or just pass on success.
        """

        # Check DSN
        if not self.getDsn():
            raise Exception("The DSN is required")

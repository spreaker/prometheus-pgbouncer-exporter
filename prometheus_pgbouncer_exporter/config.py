import yaml
import os
import re

# Define the regex used to replace $(ENV_VAR) with ENV_VAR value
ENV_VAR_MATCHER_PATTERN = re.compile(r'^(.*)\$\(([^\)]+)\)(.*)$')
ENV_VAR_REPLACER_PATTERN = re.compile(r'\$\(([^\)]+)\)')

# Define the regex used to mask the password in the DSN
DSN_PASSWORD_MASK_PATTERN = re.compile(r'^(.*:)([^@]+)(@.*)$')


class Config():
    def __init__(self):
        self.config = {}
        self.pgbouncers = False

    def getExporterHost(self):
        return self.config["exporter_host"] if "exporter_host" in self.config else "127.0.0.1"

    def getExporterPort(self):
        return self.config["exporter_port"] if "exporter_port" in self.config else 9100

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

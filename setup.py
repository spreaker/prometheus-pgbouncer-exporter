import sys
from setuptools import setup

if sys.version_info.major < 3:
    raise RuntimeError('Installing requires Python 3 or newer')

# Read the long description from README.md
with open('README.md') as file:
    long_description = file.read()

setup(
  name                          = 'prometheus-pgbouncer-exporter',
  packages                      = ['prometheus_pgbouncer_exporter'],
  version                       = '2.1.3',
  description                   = 'Prometheus exporter for PgBouncer',
  long_description              = long_description,
  long_description_content_type = "text/markdown",
  author                        = 'Spreaker Developers',
  author_email                  = 'dev@spreaker.com',
  url                           = 'https://github.com/spreaker/prometheus-pgbouncer-exporter',
  download_url                  = 'https://github.com/spreaker/prometheus-pgbouncer-exporter/archive/2.1.1.tar.gz',
  keywords                      = ['prometheus', 'pgbouncer'],
  classifiers                   = [],
  python_requires               = ' >= 3',
  install_requires              = ['psycopg2 == 2.8.5', 'prometheus_client==0.8.0', 'python-json-logger==0.1.11', 'PyYAML>=5.4.1'],
  entry_points                  = {
    'console_scripts': [
        'pgbouncer-exporter=prometheus_pgbouncer_exporter.cli:main',
    ]
  }
)

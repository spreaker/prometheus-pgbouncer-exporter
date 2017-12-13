from setuptools import setup

setup(
  name             = 'prometheus-pgbouncer-exporter',
  packages         = ['prometheus_pgbouncer_exporter'],
  version          = '0.1.0',
  description      = 'Prometheus exporter for PgBouncer',
  author           = 'Marco Pracucci',
  author_email     = 'marco@pracucci.com',
  url              = 'https://github.com/spreaker/prometheus-pgbouncer-exporter',
  download_url     = 'https://github.com/spreaker/prometheus-pgbouncer-exporter/archive/0.1.0.tar.gz',
  keywords         = ['prometheus', 'pgbouncer'],
  classifiers      = [],
  python_requires  = ' >= 3',
  install_requires = ['psycopg2 == 2.7.3.2', 'prometheus_client==0.0.21', 'python-json-logger==0.1.5'],
  entry_points     = {
    'console_scripts': [
        'pgbouncer-exporter=prometheus_pgbouncer_exporter.cli:main',
    ]
  }
)

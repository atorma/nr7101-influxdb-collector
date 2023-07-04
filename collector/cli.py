import argparse
import logging
import atexit
from .config import Config
from nr7101.nr7101 import NR7101
from influxdb_client import InfluxDBClient
from .collector import Collector
from .version import __version__


def cli():
    logging.basicConfig(level=logging.INFO, force=True)

    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description=f'NR7101 InfluxDB collector v{__version__}')
    parser.add_argument('--config-file', default=None)
    args = parser.parse_args()

    config = Config(args.config_file)
    nr7101_client = NR7101(**config.nr7101)
    influxdb_client = InfluxDBClient(**config.influxdb)
    collector = Collector(nr7101_client, influxdb_client, config.collector)

    atexit.register(on_exit, collector, influxdb_client, logger)

    collector.run()


def on_exit(collector, influxdb_client, logger):
    collector.on_exit()
    influxdb_client.close()
    logger.info('CLI exited')


if __name__ == '__main__':
    cli()

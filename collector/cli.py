import argparse
import logging
from .config import Config
from nr7101.nr7101 import NR7101
from influxdb_client import InfluxDBClient
from .collector import Collector


def cli():
    logging.basicConfig(level=logging.INFO)

    logger = logging.getLogger(__name__)

    parser = argparse.ArgumentParser(description='NR7101 InfluxDB collector')
    parser.add_argument('--config-file', default=None)
    args = parser.parse_args()

    config = Config(args.config_file)
    nr7101_client = NR7101(**config.nr7101)
    influxdb_client = InfluxDBClient(**config.influxdb)
    collector = Collector(nr7101_client, influxdb_client, config.collector)

    try:
        collector.run()
    except KeyboardInterrupt:
        influxdb_client.close()
        logger.info('Stopped')

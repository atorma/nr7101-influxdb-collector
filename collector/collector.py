import logging
import time
from ping3 import ping
from nr7101.nr7101 import NR7101
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from .config import CollectorConfig

logger = logging.getLogger(__name__)


class Collector:
    def __init__(self, nr7101_client: NR7101, influxdb_client: InfluxDBClient, config: CollectorConfig):
        self.nr7101_client = nr7101_client
        self.influxdb_client = influxdb_client
        self.influxdb_write_api = None
        self.config = config
        self.is_stopped = False
        self.nr7101_session_key = None

    def run(self):
        self.is_stopped = False
        self.influxdb_write_api = self.influxdb_client.write_api(write_options=SYNCHRONOUS)
        self.nr7101_session_key = self.nr7101_client.login()

        while True and not self.is_stopped:
            start_time_sec = time.time()
            status = None
            try:
                status = self.nr7101_client.get_status()
            except Exception as e:
                logger.warning(f'Error when getting N7101 status: {e}')

            ping_result = None
            if self.config['ping_host']:
                ping_result = ping(dest_addr=self.config['ping_host'], unit='ms', timeout=self.config['ping_timeout'])

            if status:
                try:
                    point = Point(self.config['measurement']) \
                        .tag('cellular_INTF_Current_Band', status['cellular']['INTF_Current_Band']) \
                        .field('cellular_INTF_RSSI', status['cellular']['INTF_RSSI']) \
                        .field('cellular_INTF_RSRP', status['cellular']['INTF_RSRP']) \
                        .field('cellular_INTF_RSRQ', status['cellular']['INTF_RSRQ']) \
                        .field('cellular_INTF_SINR', status['cellular']['INTF_SINR']) \
                        .field('cellular_NSA_RSSI', status['cellular']['NSA_RSSI']) \
                        .field('cellular_NSA_RSRP', status['cellular']['NSA_RSRP']) \
                        .field('cellular_NSA_RSRQ', status['cellular']['NSA_RSRQ']) \
                        .field('cellular_NSA_SINR', status['cellular']['NSA_SINR'])
                    if ping_result:
                        point = point.tag('ping_host', self.config['ping_host']) \
                            .field('ping_ms', ping_result)
                    self.influxdb_write_api.write(bucket=self.config['bucket'], record=point)
                except Exception as e:
                    logger.warning(f'Error when saving status to InfluxDB: {e}')

            duration_sec = time.time() - start_time_sec
            try:
                time.sleep(max(0.0, self.config['interval'] / 1000 - duration_sec))
            except KeyboardInterrupt:
                self.stop()

    def stop(self):
        self.is_stopped = True
        self.influxdb_write_api.flush()
        self.influxdb_write_api.close()
        if self.nr7101_session_key:
            self.nr7101_client.logout(self.nr7101_session_key)

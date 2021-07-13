import logging
import time
import typing

from ping3 import ping
from nr7101.nr7101 import NR7101
from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from .config import CollectorConfig

logger = logging.getLogger(__name__)

nr7101_tags = {
    'cellular': [
        'INTF_Current_Band',
        'INTF_Status',
        'INTF_Current_Access_Technology',
        'INTF_Cell_ID',
        'INTF_PhyCell_ID',
        'INTF_Module_Software_Version'
    ]
}
nr7101_fields = {
    'cellular': [
        'INTF_RSSI',
        'INTF_RSRP',
        'INTF_RSRQ',
        'INTF_SINR',
        'INTF_Uplink_Bandwidth',
        'INTF_Downlink_Bandwidth',
        'NSA_RSSI',
        'NSA_RSRP',
        'NSA_RSRQ',
        'NSA_SINR'
    ],
    'traffic': {
        'wwan0': [
            'BytesSent',
            'BytesReceived',
            'PacketsSent',
            'PacketsReceived',
            'ErrorsSent',
            'ErrorsReceived'
        ]
    }
}


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
        if not self.nr7101_session_key:
            self.stop()
            raise RuntimeError('NR7101 login failed')

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
                    tag_dict = flatten_status_dict(nr7101_tags, status)
                    field_dict = flatten_status_dict(nr7101_fields, status)
                    point = Point(self.config['measurement'])
                    for key, value in tag_dict.items():
                        point = point.tag(key, value)
                    for key, value in field_dict.items():
                        point = point.field(key, value)
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


def flatten_status_dict(prop_names_dict, status) -> typing.Dict:
    flattened_dict = dict()
    for parent_key, keys in prop_names_dict.items():
        if isinstance(keys, list):
            for key in keys:
                value = status[parent_key][key]
                flattened_dict[key] = value
        elif isinstance(keys, dict):
            nested_dict = flatten_status_dict(keys, status[parent_key])
            for key, value in nested_dict.items():
                flattened_dict[key] = value
        else:
            raise ValueError(f'Value of {parent_key} must be an array or a dict')
    return flattened_dict

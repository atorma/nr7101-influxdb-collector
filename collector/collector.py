import logging
import typing
import rx
from rx import operators as ops
from datetime import timedelta, datetime
from ping3 import ping
from nr7101.nr7101 import NR7101
from influxdb_client import InfluxDBClient, Point, WriteOptions
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
        self.config = config
        self.nr7101_session_key = None
        self.influxdb_write_api = influxdb_client.write_api(write_options=WriteOptions(
            batch_size=1,
            retry_interval=config['interval'],
            max_retry_time=config['influxdb_max_retry_time'],
            max_retries=config['influxdb_max_retries'],
            max_retry_delay=config['influxdb_max_retry_delay'],
            exponential_base=config['influxdb_exponential_base']
        ))

    def run(self):
        self.nr7101_session_key = self.nr7101_client.login()
        if not self.nr7101_session_key:
            raise RuntimeError('NR7101 login failed')

        influxdb_data_obs = rx \
            .interval(period=timedelta(milliseconds=self.config['interval'])) \
            .pipe(ops.map(lambda i: (datetime.utcnow(), self._get_status())),
                  ops.map(lambda data: (data[0], data[1], self._get_ping())),
                  ops.map(lambda data: self._get_data_point(data[0], data[1], data[2])))

        self.influxdb_write_api.write(bucket=self.config['bucket'], record=influxdb_data_obs)

        influxdb_data_obs.run()

    def _get_status(self) -> typing.Optional[dict]:
        try:
            return self.nr7101_client.get_status()
        except Exception as e:
            logger.warning(f'Error when getting N7101 status: {e}')
            return None

    def _get_ping(self) -> typing.Optional[float]:
        try:
            return ping(dest_addr=self.config['ping_host'], unit='ms', timeout=self.config['ping_timeout'])
        except Exception as e:
            logger.warning(f'Error when pinging {self.config["ping_host"]}: {e}')
            return None

    def _get_data_point(self,
                        utc_time: datetime,
                        status: typing.Optional[dict],
                        ping_result: typing.Optional[float]
                        ) -> Point:
        point = Point(self.config['measurement']).time(utc_time)

        if status:
            tag_dict = flatten_status_dict(nr7101_tags, status)
            field_dict = flatten_status_dict(nr7101_fields, status)
            for key, value in tag_dict.items():
                point = point.tag(key, value)
            for key, value in field_dict.items():
                point = point.field(key, value)

        if ping_result:
            point = point \
                .tag('ping_host', self.config['ping_host']) \
                .field('ping_ms', ping_result)

        return point

    def on_exit(self):
        if self.influxdb_write_api:
            self.influxdb_write_api.close()
            logger.info('InfluxDB write api closed')
        if self.nr7101_session_key:
            self.nr7101_client.logout(self.nr7101_session_key)
            logger.info('Logged out from NR7101')
        logger.info('Collector exited')


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

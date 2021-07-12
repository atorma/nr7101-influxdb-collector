import typing
import os
from configparser import ConfigParser


class NR7101Config(typing.TypedDict):
    url: str
    username: str
    password: str


class InfluxDbConfig(typing.TypedDict):
    url: str
    org: typing.Optional[str]
    token: str
    timeout: int
    verify_ssl: typing.Optional[bool]
    connection_pool_maxsize: typing.Optional[int]
    auth_basic: typing.Optional[bool]


class CollectorConfig(typing.TypedDict):
    interval: int
    bucket: str
    measurement: str
    ping_host: typing.Optional[str]
    ping_timeout: int


class Config:
    def __init__(self, config_file_path: typing.Optional[str] = None):
        config = ConfigParser()
        config.read_dict({
            'nr7101': {},
            'influx2': {},
            'collector': {
                'interval': 5000,
                'measurement': 'status'
            }})

        if config_file_path:
            config.read(config_file_path)

        def parse_option(env_var: str, section: str, option: str, **kwargs) -> typing.Any:
            value = None
            if env_var in os.environ:
                value = os.environ[env_var]
            elif config.has_option(section, option):
                value = config[section][option]

            default = kwargs.get('default', None)
            is_required = kwargs.get('required', False)
            parse = kwargs.get('parser', str)

            if not value and not is_required:
                return default
            elif not value and is_required:
                raise ValueError(f'Missing environment variable {env_var} or config file option [{section}] {option}')

            return parse(value)

        self.nr7101: NR7101Config = {
            'url': parse_option('NR7101_URL', 'nr7101', 'url', required=True),
            'username': parse_option('NR7101_USERNAME', 'nr7101', 'username', required=True),
            'password': parse_option('NR7101_PASSWORD', 'nr7101', 'password', required=True),
        }

        self.influxdb: InfluxDbConfig = {
            'url': parse_option('INFLUXDB_V2_URL', 'influx2', 'url', required=True),
            'org': parse_option('INFLUXDB_V2_ORG', 'influx2', 'org', default=None),
            'token': parse_option('INFLUXDB_V2_TOKEN', 'influx2', 'token', default='auth-token'),
            'timeout': parse_option('INFLUXDB_V2_TIMEOUT', 'influx2', 'timeout', default=4000, parser=int),
            'verify_ssl': parse_option('INFLUXDB_V2_VERIFY_SSL', 'influx2', 'verify_ssl', default=True,
                                       parser=parse_bool),
            'connection_pool_maxsize': parse_option('INFLUXDB_V2_CONNECTION_POOL_MAXSIZE', 'influx2',
                                                    'connection_pool_maxsize', default=None, parser=int),
            'auth_basic': parse_option('INFLUXDB_V2_AUTH_BASIC', 'influx2', 'auth_basic', default=False,
                                       parser=parse_bool),
        }

        self.collector: CollectorConfig = {
            'interval': parse_option('COLLECTOR_INTERVAL', 'collector', 'interval', default=5000, parser=int),
            'bucket': parse_option('COLLECTOR_BUCKET', 'collector', 'bucket', required=True),
            'measurement': parse_option('COLLECTOR_MEASUREMENT', 'collector', 'measurement', required=True),
            'ping_host': parse_option('COLLECTOR_PING_HOST', 'collector', 'ping_host'),
            'ping_timeout': parse_option('COLLECTOR_PING_TIMEOUT', 'collector', 'ping_timeout', default=1,
                                         parser=int)
        }


def parse_bool(value):
    return str(value).lower in ['true', 'yes']

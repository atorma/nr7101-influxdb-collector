import typing
import os
import math
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
    profilers: typing.Optional[str]
    default_tags: dict


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
            'collector': {}
        })

        if config_file_path:
            config.read(config_file_path)

        def option(env_var: str, **kwargs):
            return parse_option_value(config, env_var, **kwargs)

        self.nr7101: NR7101Config = {
            'url': option('NR7101_URL', required=True),
            'username': option('NR7101_USERNAME', required=True),
            'password': option('NR7101_PASSWORD', required=True),
        }

        self.collector: CollectorConfig = {
            'interval': option('COLLECTOR_INTERVAL', default=5000, parser=int),
            'bucket': option('COLLECTOR_BUCKET', required=True),
            'measurement': option('COLLECTOR_MEASUREMENT', required=True),
            'ping_host': option('COLLECTOR_PING_HOST'),
            'ping_timeout': option('COLLECTOR_PING_TIMEOUT', default=1, parser=int)
        }

        self.influxdb: InfluxDbConfig = {
            'url': option('INFLUXDB_V2_URL', required=True),
            'org': option('INFLUXDB_V2_ORG'),
            'token': option('INFLUXDB_V2_TOKEN', default='auth-token'),
            'timeout': option('INFLUXDB_V2_TIMEOUT', default=math.ceil(self.collector['interval'] * 0.75), parser=int),
            'verify_ssl': option('INFLUXDB_V2_VERIFY_SSL', default=True, parser=parse_bool),
            'connection_pool_maxsize': option('INFLUXDB_V2_CONNECTION_POOL_MAXSIZE', parser=int),
            'auth_basic': option('INFLUXDB_V2_AUTH_BASIC', default=False, parser=parse_bool),
            'profilers': option('INFLUXDB_V2_PROFILERS'),
            'default_tags': parse_default_tags(config)
        }


def parse_option_value(config: ConfigParser, env_var: str, **kwargs) -> typing.Any:
    if env_var.startswith('INFLUXDB_V2_'):
        prefix = 'INFLUXDB_V2_'
        section = 'influx2'
    elif env_var.startswith('NR7101_'):
        prefix = 'NR7101_'
        section = 'nr7101'
    elif env_var.startswith('COLLECTOR_'):
        prefix = 'COLLECTOR_'
        section = 'collector'
    else:
        raise ValueError(f'Cannot handle environment variable {env_var}')

    option = env_var.replace(prefix, '', 1).lower()

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


def parse_default_tags(config: ConfigParser) -> dict:
    default_tags = dict()
    if config.has_section('tags'):
        tags = {k: v.strip('"') for k, v in config.items('tags')}
        default_tags = dict(tags)
    for key, value in os.environ.items():
        if key.startswith("INFLUXDB_V2_TAG_"):
            default_tags[key[16:].lower()] = value
    return default_tags


def parse_bool(value):
    return str(value).lower in ['true', 'yes']

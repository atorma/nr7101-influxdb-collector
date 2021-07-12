# Zyxel NR7101 InfluxDB collector

## Requirements

InfluxDB version 1.8+ or 2.0+.

## Installation

```sh
pip3 install git+https://github.com/atorma/nr7101-influxdb-collector.git
```

## Usage

**Note!** Use the https protocol in NR7101 URL. Authentication does not work when using http.

Using configuration file:

```sh
nr7101-collector --config-file=/path/to/config.ini
```

config.ini
```
# See https://pypi.org/project/influxdb-client for full list
[influx2]
url=http://localhost:8086
org=my-org
token=my-token

[nr7101]
url=https://192.168.1.1
username=admin
password=my-password

[collector]
interval=5000
bucket=nr7101
measurement=status
```

Using environment variables (see [https://pypi.org/project/influxdb-client](https://pypi.org/project/influxdb-client) 
for InfluxDB client environment variables):

```sh
INFLUXDB_V2_URL=http://localhost:8086 \
 INFLUXDB_V2_ORG=my-org \
 INFLUXDB_V2_TOKEN=my-token \
 NR7101_URL=https://192.168.1.1 \
 NR7101_USERNAME=admin \
 NR7101_PASSWORD=my-password \
 COLLECTOR_BUCKET=nr7101 \
 COLLECTOR_MEASUREMENT=status \
 nr7101-collector
```

Using both environment variables and config file (the former take precedence):

```sh
 INFLUXDB_V2_TOKEN=my-token NR7101_PASSWORD=my-password nr7101-collector --config-file=/path/to/config.ini
```
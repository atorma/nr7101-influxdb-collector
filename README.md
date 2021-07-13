# Zyxel NR7101 InfluxDB collector

## Requirements

InfluxDB version 1.8+ or 2.0+. See [InfluxDB 1.8 API compatibility](https://github.com/influxdata/influxdb-client-python#influxdb-18-api-compatibility).

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
[influx2]
url=http://localhost:8086
org=my-org
token=my-token

[tags]
my_tag=my_default_value
other_tag=other_tag_default_value

[nr7101]
url=https://192.168.1.1
username=admin
password=my-password

[collector]
interval=5000
bucket=nr7101
measurement=status
ping_host=google.com
ping_timeout=1
```

Using environment properties (see [https://pypi.org/project/influxdb-client](https://pypi.org/project/influxdb-client) 
for InfluxDB client environment properties):

```sh
INFLUXDB_V2_URL=http://localhost:8086 \
 INFLUXDB_V2_ORG=my-org \
 INFLUXDB_V2_TOKEN=my-token \
 NR7101_URL=https://192.168.1.1 \
 NR7101_USERNAME=admin \
 NR7101_PASSWORD=my-password \
 COLLECTOR_BUCKET=nr7101 \
 COLLECTOR_MEASUREMENT=status \
 COLLECTOR_PING_HOST=google.com \
 nr7101-collector
```

Using both environment properties and config file (the former take precedence):

```sh
 INFLUXDB_V2_TOKEN=my-token NR7101_PASSWORD=my-password nr7101-collector --config-file=/path/to/config.ini
```

## Configuration 

### [influx2]

See [https://github.com/influxdata/influxdb-client-python](https://github.com/influxdata/influxdb-client-python).
For InfluxDB 1.8+ see [API compatibility](https://github.com/influxdata/influxdb-client-python#influxdb-18-api-compatibility).

### [tags]

Optional [default tags](https://github.com/influxdata/influxdb-client-python#default-tags) to add to all data points. Can also be given as environment properties.

### [nr7101]

* `url` / `NR7101_URL` - The https URL of the NR7101 web interface. Required.
* `username` / `NR7101_USERNAME`: The username of the NR7101 user. Required.
* `password` / `NR7101_PASSWORD`: The password of the NR7101 user. Required.

### [collector]

* `interval` / `COLLECTOR_INTERVAL`: Interval, in milliseconds, of data collection. Default is `5000`.
* `bucket` / `COLLECTOR_BUCKET`: InfluxDB bucket name to store data in. Required.
  * See also [InfluxDB 1.8 API compatibility](https://github.com/influxdata/influxdb-client-python#influxdb-18-api-compatibility).
* `measurement` / `COLLECTOR_MEASUREMENT`: InfluxDB measurement name. Required.
* `ping_host` / `COLLECTOR_PING_HOST`: Optional hostname for ping measurements. Default is `None` meaning ping is not measured.
* `ping_timeout` / `COLLECTOR_PING_TIMEOUT`: Ping timeout in seconds. Default is `1`. 
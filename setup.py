from setuptools import setup, find_packages
from collector.version import __version__

setup(
    name='nr7101-influxdb-collector',
    version=__version__,
    description='Zyxel NR7101 InfluxDB Collector',
    author='Anssi Törmä',
    license='MIT',
    url='https://github.com/atorma/nr7101-influxdb-collector',
    packages=find_packages(),
    install_requires=[
        'ping3==2.9.1',
        'influxdb-client==1.19.0',
        'nr7101 @ git+https://github.com/pkorpine/nr7101.git@v1.3.0',
        'rx==3.2.0'
    ],
    entry_points={
        'console_scripts': ['nr7101-collector=collector.cli:cli'],
    },
)

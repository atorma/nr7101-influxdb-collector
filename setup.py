from setuptools import setup, find_packages

setup(
    name='nr7101-influxdb-collector',
    version='2.1.1',
    description='Zyxel NR7101 InfluxDB Collector',
    author='Anssi Törmä',
    license='MIT',
    url='https://github.com/atorma/nr7101-influxdb-collector',
    packages=find_packages(),
    install_requires=[
        'ping3',
        'influxdb-client[ciso]',
        'nr7101 @ git+https://github.com/pkorpine/nr7101.git@v1.3.0',
        'rx'
    ],
    entry_points={
        'console_scripts': ['nr7101-collector=collector.cli:cli'],
    },
)

from setuptools import setup, find_packages

setup(
    name='nr7101-influxdb-collector',
    version='1.0.0',
    description='Zyxel NR7101 InfluxDB Collector',
    author='Anssi Törmä',
    license='MIT',
    url='https://github.com/atorma/nr7101',
    packages=find_packages(),
    install_requires=[
        'ping3',
        'influxdb-client[ciso]',
        'nr7101 @ git+https://github.com/pkorpine/nr7101.git'
    ],
    entry_points={
        'console_scripts': ['nr7101-collector=collector.cli:cli'],
    },
)
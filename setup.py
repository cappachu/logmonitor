
from setuptools import setup, find_packages
import logmonitor

setup(
    name='logmonitor',
    version=logmonitor.__version__,
    description='Monitors a w3c log file',
    author='Codanda B. Appachu',
    url='https://github.com/mtamrf/logmonitor',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'logmonitor = logmonitor.logmonitor:main',
        ]
    },
    install_requires=[
        'argparse',
        'clint',
    ],
)

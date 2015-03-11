try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import logmonitor

setup(
    name='logmonitor',
    version=logmonitor.__version__,
    description='Monitors a w3c log file',
    author='Codanda B. Appachu',
    author_email='mtamrf@gmail.com',
    url='https://github.com/mtamrf/logmonitor',
    entry_points={
        'console_scripts': [
            'logmonitor = logmonitor.logmonitor:main',
        ]
    },
    install_requires=[
        'argparse',
        'pytest',
        'clint',
    ],
)

#!/usr/bin/env python3

from setuptools import setup

setup(
        name='pyelectronics',
        version='0.1.2',
        packages=['electronics', 'electronics.devices', 'electronics.gateways'],
        url='https://github.com/MartijnBraam/pyElectronics',
        license='MIT',
        author='Martijn Braam',
        author_email='martijn@brixit.nl',
        description='Python 3 library for working with electronics',
        keywords=["electronics", "spi", "i2c", "buspirate"],
        classifiers=[
            "Programming Language :: Python",
            "Programming Language :: Python :: 3",
            "Development Status :: 4 - Beta",
            "Operating System :: POSIX :: Linux",
            "License :: OSI Approved :: MIT License"
        ],
)

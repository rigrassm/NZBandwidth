# -*- coding: utf-8 -*-
from distutils.core import setup

setup(
    name='NZBandwidth',
    version='0.1.0',
    author='Ricky Grassmuck',
    author_email='rigrassm@gmail.com',
    packages=['nzbandwidth'],
    url='https://github.com/rigrassm/NZBandwidth',
    license='LICENSE.txt',
    description='Application for managing NZBGet download speeds dynamically',
    long_description=open('README.md').read(),
    install_requires=['requests >= 2.12.5']
)

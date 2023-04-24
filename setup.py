from setuptools import setup, find_packages
from os import path

import versioneer

NAME = 'dart-fss'

with open(path.join('./', 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    long_description=long_description,
    long_description_content_type='text/markdown',
)

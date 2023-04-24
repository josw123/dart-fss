from setuptools import setup

import versioneer

NAME = 'dart-fss'

setup(
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
)

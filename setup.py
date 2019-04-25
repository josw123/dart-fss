from setuptools import setup, find_packages
from os import path

import versioneer

NAME = 'dart-fss'

INSTALL_REQUIRES = (
    ['numpy', 'pandas', 'requests', 'lxml', 'tqdm', 'beautifulsoup4', 'isodate', 'arelle', 'fake-useragent']
)


with open(path.join('./', 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name=NAME,
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Web-scraping http://dart.fss.or.kr',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Sungwoo Jo',
    author_email='nonswing.z@gmail.com',
    url='https://github.com/josw123/dart-fss',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3 :: Only'
    ],
    packages=find_packages(exclude=['dart_fss.tests']),
    keywords=['fss', 'dart-fss', 'scrapping'],
    python_requires='>=3.5',
    package_data={},
    install_requires=INSTALL_REQUIRES
)

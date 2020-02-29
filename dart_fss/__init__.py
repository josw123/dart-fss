# -*- coding: utf-8 -*-
from dart_fss import api, auth, corp, errors, filings, fs, utils, xbrl
from dart_fss.auth import set_api_key, get_api_key
from dart_fss.corp import get_corp_list
from dart_fss.filings import search
from dart_fss.fs import extract
from dart_fss.xbrl import get_xbrl_from_file

__all__ = [
    'api',
    'auth', 'set_api_key', 'get_api_key',
    'corp', 'get_corp_list',
    'errors',
    'filings', 'search',
    'fs', 'extract',
    'utils',
    'xbrl', 'get_xbrl_from_file'
]

from ._version import get_versions
__version__ = get_versions()['version']

del get_versions

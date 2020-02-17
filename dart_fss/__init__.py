# -*- coding: utf-8 -*-
from dart_fss import api, auth, corp, errors, filings, fs, utils, xbrl
__all__ = [
    'api',
    'auth',
    'corp',
    'errors',
    'filings',
    'fs',
    'utils',
    'xbrl',
]

from ._version import get_versions
__version__ = get_versions()['version']

del get_versions

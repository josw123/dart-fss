# -*- coding: utf-8 -*-
from .search import search_report
from .crp import get_crp_info, get_crp_list, search_crp
from .auth import dart_set_api_key

__all__ = ['search_report', 'get_crp_info', 'get_crp_list', 'search_crp', 'dart_set_api_key']

from ._version import get_versions
__version__ = get_versions()['version']

del get_versions

# -*- coding: utf-8 -*-
from .cache import cache
from .datetime import get_datetime, check_datetime
from .file import unzip, search_file, create_folder
from .notebook import dict_to_html, is_notebook
from .request import get_user_agent, query_to_regex, request
from .singleton import Singleton
from .string import str_compare, str_insert_whitespace, str_unit_to_number_unit

__all__ = ['cache', 'get_datetime', 'check_datetime', 'unzip',
           'search_file', 'create_folder', 'dict_to_html',
           'is_notebook', 'get_user_agent', 'query_to_regex', 'request',
           'Singleton', 'str_compare', 'str_insert_whitespace', 'str_unit_to_number_unit']
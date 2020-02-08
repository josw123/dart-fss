# -*- coding: utf-8 -*-
from .cache import cache
from .datetime import get_datetime, check_datetime
from .file import unzip, xml_to_dict, search_file, create_folder, get_cache_folder
from .notebook import dict_to_html, is_notebook
from .request import get_user_agent, query_to_regex, request
from .singleton import Singleton
from .spinner import Spinner
from .string import str_compare, str_insert_whitespace, str_unit_to_number_unit
from .regex import is_operator, precedence, infix_to_postfix, str_to_regex, str_to_pattern


__all__ = ['cache', 'get_datetime', 'check_datetime', 'unzip', 'xml_to_dict',
           'search_file', 'create_folder', 'get_cache_folder', 'dict_to_html',
           'is_notebook', 'get_user_agent', 'query_to_regex', 'request',
           'Singleton', 'Spinner', 'str_compare', 'str_insert_whitespace',
           'str_unit_to_number_unit', 'is_operator', 'precedence',
           'infix_to_postfix', 'str_to_regex', 'str_to_pattern']
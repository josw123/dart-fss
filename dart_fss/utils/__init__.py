# -*- coding: utf-8 -*-
from dart_fss.utils.cache import cache
from dart_fss.utils.datetime import get_datetime, check_datetime
from dart_fss.utils.file import unzip, xml_to_dict, search_file, create_folder, get_cache_folder
from dart_fss.utils.notebook import dict_to_html, is_notebook
from dart_fss.utils.request import get_user_agent, query_to_regex, request
from dart_fss.utils.singleton import Singleton
from dart_fss.utils.spinner import Spinner, spinner_enable
from dart_fss.utils.string import str_compare, str_insert_whitespace, str_unit_to_number_unit, str_upper, get_currency_str
from dart_fss.utils.regex import is_operator, precedence, infix_to_postfix, str_to_regex, str_to_pattern
from dart_fss.utils.dataframe import dataframe_astype


__all__ = ['cache', 'get_datetime', 'check_datetime', 'unzip', 'xml_to_dict',
           'search_file', 'create_folder', 'get_cache_folder', 'dict_to_html',
           'is_notebook', 'get_user_agent', 'query_to_regex', 'request',
           'Singleton', 'Spinner', 'spinner_enable', 'str_compare', 'str_insert_whitespace',
           'str_unit_to_number_unit', 'get_currency_str', 'str_upper', 'is_operator', 'precedence',
           'infix_to_postfix', 'str_to_regex', 'str_to_pattern', 'dataframe_astype']
# -*- coding: utf-8 -*-

from dart_fss.utils import Singleton, query_to_regex
from dart_fss.api.filings import get_corp_code


class CorpList(object, metaclass=Singleton):

    def __init__(self):
        self._corps = None

    def load(self):
        self._corps = get_corp_code()

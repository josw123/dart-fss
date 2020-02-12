# -*- coding: utf-8 -*-
import re

from dart_fss.utils import Singleton
from dart_fss.api.filings import get_corp_code
from dart_fss.corp.corp import Corp


class CorpList(object, metaclass=Singleton):

    def __init__(self, profile=False):
        self._corps = None
        self._corp_codes = dict()
        self._corp_names = []
        self._stock_codes = dict()
        self._profile = profile

    def load(self, profile=False):
        self._corps = [Corp(**x, profile=profile) for x in get_corp_code()]
        for idx, x in enumerate(self._corps):
            self._corp_codes[x.corp_code] = idx
            self._corp_names.append(x.corp_name)
            if x.stock_code is not None:
                self._stock_codes[x.stock_code] = idx

    @property
    def corps(self):
        """ 모든 상장된 종목(회사)를 반환한다 """
        if self._corps is None:
            self.load(profile=self._profile)
        return self._corps

    def find_by_corp_code(self, corp_code):
        corps = self.corps
        idx = self._corp_codes.get(corp_code)
        return corps[idx] if idx is not None else None

    def find_by_corp_name(self, corp_name, exactly=False):
        corps = self.corps
        res = []
        if exactly is True:
            corp_name = '^' + corp_name + '$'
        regex = re.compile(corp_name)
        for idx, corp_name in enumerate(self._corp_names):
            if regex.search(corp_name) is not None:
                res.append(corps[idx])
        return res if len(res) > 0 else None

    def find_by_stock_code(self, stock_code):
        corps = self.corps
        idx = self._stock_codes.get(stock_code)
        return corps[idx] if idx is not None else None

    def __repr__(self):
        corps = self.corps
        return 'Number of companies: {}'.format(len(corps))

    def __getitem__(self, item):
        corps = self.corps
        return corps[item]

    def __len__(self):
        corps = self.corps
        return len(corps)
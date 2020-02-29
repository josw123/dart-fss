# -*- coding: utf-8 -*-
import re

from dart_fss.utils import Singleton, Spinner
from dart_fss.api.filings import get_corp_code
from dart_fss.corp.corp import Corp


def get_corp_list():
    """ DART 공시된 회사 리스트 반환

    Returns
    -------
    CorpList
        회사 리스트
    """
    return CorpList()


class CorpList(object, metaclass=Singleton):

    def __init__(self, profile=False):
        """ CorpList 초기화

        Parameters
        ----------
        profile: bool
            Corp Class 반환시 Profile 자동 로딩 여부
        """
        self._corps = None
        self._corp_codes = dict()
        self._corp_names = []
        self._stock_codes = dict()
        self._profile = profile

    def load(self, profile=False):
        """ 회사 정보 로딩

        Parameters
        ----------
        profile: bool, optional
            상세정보 로딩 여부
        """
        spinner = Spinner('Loading CorpList')
        spinner.start()
        self._corps = [Corp(**x, profile=profile) for x in get_corp_code()]
        for idx, x in enumerate(self._corps):
            self._corp_codes[x.corp_code] = idx
            self._corp_names.append(x.corp_name)
            if x.stock_code is not None:
                self._stock_codes[x.stock_code] = idx
        spinner.stop()

    @property
    def corps(self):
        """ 모든 상장된 종목(회사)를 반환한다 """
        if self._corps is None:
            self.load(profile=self._profile)
        return self._corps

    def find_by_corp_code(self, corp_code):
        """ DART에서 사용하는 회사 코드를 이용한 찾기

        Parameters
        ----------
        corp_code: str
            공시대상회사의 고유번호(8자리)

        Returns
        -------
        Corp
            회사 정보를 담고 있는 클래스
        """
        corps = self.corps
        idx = self._corp_codes.get(corp_code)
        return corps[idx] if idx is not None else None

    def find_by_corp_name(self, corp_name, exactly=False):
        """ 회사 명칭을 이용한 검색

        Parameters
        ----------
        corp_name: str
            공시대상회사의 고유번호(8자리)
        exactly: bool, optional
            corp_name과 정확히 일치 여부(default: False)

        Returns
        -------
        Corp
            회사 정보를 담고 있는 클래스
        """
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
        """ 주식 종목 코드를 이용한 찾기

        Parameters
        ----------
        stock_code: str
            주식 종목 코드(6자리)

        Returns
        -------
        Corp
            회사 정보를 담고 있는 클래스
        """
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
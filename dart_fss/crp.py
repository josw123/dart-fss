# -*- coding: utf-8 -*-
from typing import Union, List, Dict
from bs4 import BeautifulSoup

from pandas import DataFrame

from ._utils import Singleton, dict_to_html, request_get, query_to_regex
from .auth import DartAuth
from .markets import get_market_name
from .errors import check_err_code
from .search import search_report, SearchResults
from .fs import search_financial_statement

str_or_list = Union[str, List[str]]


class Crp(object):
    """ 회사(종목) 정보

    회사(종목)의 정보를 담고 있는 클래스. 종목 코드, 이름, 종목 분류 및 취급 물품에 관한 기본정보를 가지고 있으며
    DART 에서 제공하는 기업개황 정보를 담고 있다.

    Attributes
    ----------
    crp_cd: str
        종목 코드
    crp_nm: str
        종목 이름
    crp_ctp: str
        종목 분류
    crp_prod: str
        종목의 취급 물품

    """
    _SEARCH_URL_ = 'http://dart.fss.or.kr/api/'

    def __init__(self, crp_cd: str, lazy_loading: bool = True, **kwargs):
        """ 종목 정보 초기화

        Parameters
        ----------
        crp_cd: str
            종목 코드
        lazy_loading: bool
            True 일때 Lazy loading, False 일때 즉시 loading
        **kwargs
            기타 종목 정보

        """
        self.crp_cd = crp_cd
        self.crp_nm = kwargs.get('crp_nm')
        self.crp_ctp = kwargs.get('crp_ctp')
        self.crp_prod = kwargs.get('crp_prod')

        self._info = None
        if lazy_loading is False:
            self.load()

    def load(self) -> None:
        """ 종목 정보 로딩 """
        api_key = DartAuth().api_key

        url = self._SEARCH_URL_ + 'company.json'
        params = dict(
            auth=api_key,
            crp_cd=self.crp_cd
        )
        resp = request_get(url=url, params=params)
        data = resp.json()
        data['crp_cd'] = data.pop('stock_cd')
        check_err_code(**data)
        self.crp_nm = data.get('crp_nm')
        self._info = {key: value for key, value in data.items()
                      if key not in ['err_code', 'err_msg', 'crp_cd', 'crp_nm']}

    @property
    def info(self) -> Dict[str, str]:
        """ dict of str: 종목 정보 반환 """
        if self._info is None:
            self.load()
        return self._info

    def to_dict(self) -> Dict[str, str]:
        """ 종목에 관한 모든 정보 반환

        Returns
        -------
        dict of str
            종목에 관한 모든 정보 반환

        """
        info = self.info
        res = dict()

        res['crp_cd'] = self.crp_cd
        res['crp_nm'] = self.crp_nm

        for key, value in info.items():
            res[key] = value

        res['crp_ctp'] = self.crp_ctp
        res['crp_prod'] = self.crp_prod
        return res

    def __repr__(self) -> str:
        result = '[{}]{}'.format(self.crp_cd, self.crp_nm)
        return result

    def _repr_html_(self) -> str:
        return dict_to_html(self.to_dict(), header=['Label', 'Data'])

    def search_report(self, start_dt: str = None, end_dt: str = None, fin_rpt: bool = False,
                      dsp_tp: str_or_list = None, bsn_tp: str_or_list = None, sort: str = 'date',
                      series: str = 'desc', page_no: int = 1, page_set: int = 10) -> SearchResults:
        """ 종목에 관한 DART 공시 정보 검색

        Parameters
        ----------
        start_dt: str
            검색 시작일자(YYYYMMDD)
        end_dt: str
            검색 종료일자(YYYYMMDD)
        fin_rpt: bool
            최종보고서만 검색여부, 기본값: False
        dsp_tp: str
            공시 유형(DSP_TYPES)
        bsn_tp: str or list of str
            공시 상세 유형(BSN_TYPES)
        sort: str
            정렬 방법, 접수일자(date), 회사명(crp), 보고서명(rpt), 기본값 : date
        series: str
            오름차순(asc), 내림차순(desc) 기본값 : desc
        page_no: int
            페이지 번호, 기본값: 1
        page_set: int
            페이지당 건수(1-100) 기본값: 10, 최대값: 100

        Returns
        -------
        SearchResults
            검색결과

        """

        return search_report(self.crp_cd, start_dt, end_dt, fin_rpt, dsp_tp,
                             bsn_tp, sort, series, page_no, page_set)

    def get_financial_statement(self, start_dt: str, end_dt: str = None, fs_tp: str = 'fs', separate: bool = False,
                                report_tp: str = 'annual', lang: str = 'ko', show_abstract: bool = False,
                                show_class: bool = True, show_depth: int = 10, show_concept: bool = True,
                                separator: bool = True) -> DataFrame:
        """ 재무제표 검색

        Parameters
        ----------
        start_dt: str
            검색 시작일자(YYYYMMDD)
        end_dt: str
            검색 종료일자(YYYYMMDD)
        fs_tp: str
            리포트 종류
        separate: bool
            개별지업 여뷰
        report_tp: str
            'annual' 1년, 'half' 반기, 'quarter' 분기
        lang: str
            'ko' 한글, 'en' 영문
        show_abstract: bool
            abstract 표기 여부
        show_class: bool
            class 표기 여부
        show_depth: int
            class 표시 깊이
        show_concept: bool
            concept 표시 여부
        separator: bool
            1000단위 구분자 표시 여부

        Returns
        -------
        DataFrame
            제무제표 검색 결과

        """
        return search_financial_statement(self.crp_cd, start_dt, end_dt=end_dt, fs_tp=fs_tp, separate=separate,
                                          report_tp=report_tp, lang=lang, show_abstract=show_abstract,
                                          show_class=show_class, show_depth=show_depth, show_concept=show_concept,
                                          separator=separator)


class CrpList(object):
    """ 상장된 종목(회사) 리스트

    지정된 시장의 상장된 종목(회사)를 모두 불러온다.

    Attributes
    ----------
    market_type: str
        시장 종류

    """
    _COMPANY_LIST_URL_ = 'http://kind.krx.co.kr/corpgeneral/corpList.do'

    def __init__(self, market_type: str = 'allMkt'):
        """ CrpList 클래스 초기화시 시장을 지정하지 않으면 모든 시장정보를 불러 온다

        Parameters
        ----------
        market_type: str, optional
            시장 종류

        """
        self.market_type = market_type
        self.__crp_list = []
        self._load()

    def _load(self):
        url = '{}?method=download&searchType=13'.format(self._COMPANY_LIST_URL_)
        if self.market_type == 'allMkt':
            pass
        elif self.market_type == 'etcMkt':
            raise ValueError('ETC market is not supported')
        else:
            url = '{}&marketType={}'.format(url, self.market_type)
        resp = request_get(url=url, timeout=120)
        soup = BeautifulSoup(resp.text, 'html.parser')
        rows = soup.find_all('tr')
        for row in rows:
            cols = row.find_all('td')
            if len(cols) > 0:
                crp_nm = cols[0].text.strip()
                crp_cd = cols[1].text.strip()
                crp_ctp = cols[2].text.strip()
                crp_prod = cols[3].text.strip()
                crp_info = {'crp_cd': crp_cd, 'crp_nm': crp_nm, 'crp_ctp': crp_ctp, 'crp_prod': crp_prod}
                self.__crp_list.append(Crp(**crp_info))

    @property
    def crp_list(self) -> List[Crp]:
        """list of Crp: 모든 상장된 종목(회사)를 반환한다."""
        if len(self.__crp_list) == 0:
            self._load()
        return self.__crp_list

    def find_by_name(self, query: str_or_list) -> List[Crp]:
        """ 회사 이름에 특정 단어가 포함된 회사들을 반환한다

        Parameters
        ----------
        query: str or list of str
            검색식

        Returns
        -------
        list of Crp
            검색된 회사 리스트

        """
        regex = query_to_regex(query)
        query_res = [crp for crp in self.crp_list if len(regex.findall(crp.crp_nm)) > 0]
        return query_res

    def find_by_product(self, query: str_or_list) -> List[Crp]:
        regex = query_to_regex(query)
        query_res = [crp for crp in self.crp_list if len(regex.findall(crp.crp_prod + crp.crp_ctp)) > 0]
        return query_res

    def find_by_crp_cd(self, crp_cd: str) -> Crp:
        query_res = [crp for crp in self.crp_list if crp.crp_cd == crp_cd]
        return query_res[0] if len(query_res) > 0 else None

    def __repr__(self):
        return 'Narket type: {}\nNumber of companies: {}'.format(self.market_type, len(self.crp_list))

    def __getitem__(self, item):
        return self.crp_list[item]


def get_crp_list(market: str = None) -> CrpList:
    """ 상장된 회사 리스트를 반환하는 함수

    market parameter 가 None 일 경우 모든 상장된 회사 리스트를 반환함

    Parameters
    ----------
    market: str
        CRP_TYPES 참고

    Returns
    -------
    CrpList
        상장된 증권 리스트

    """
    return _CrpTools().get_crp_list(market)


def get_crp_info(crp_cd: str = None) -> Crp:
    """ 회사(증권) 정보를 반환하는 함수

    Parameters
    ----------
    crp_cd: str
        종목 코드

    Returns
    -------
    Crp
        회사 정보

    """
    crp_list = _CrpTools().get_crp_list()
    return crp_list.find_by_crp_cd(crp_cd)


def search_crp(crp_nm: str = None, market: str = None) -> List[Crp]:
    """ 회사(증권) 종목 코드를 반환하는 함수

    Parameters
    ----------
    crp_nm: str
        종목명
    market: str
        CRP_TYPES 참고

    Returns
    -------
    list of Crp
        Crp 리스트 반환

    """
    crp_list = _CrpTools().get_crp_list(market)
    return crp_list.find_by_name(crp_nm)


class _CrpTools(object, metaclass=Singleton):
    def __init__(self):
        self.__crp_list = []

    def get_crp_list(self, market: str = None) -> CrpList:
        market_type = get_market_name(market)
        if len(self.__crp_list) > 0:
            for tp, crp_list in self.__crp_list:
                if market_type == tp:
                    return crp_list

        new_crp_list = CrpList(market_type)
        self.__crp_list.append((market_type, new_crp_list))
        return new_crp_list

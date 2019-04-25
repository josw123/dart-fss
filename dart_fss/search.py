# -*- coding: utf-8 -*-

import re

from datetime import datetime
from collections import OrderedDict
from typing import Union, Dict, List

from .auth import DartAuth
from .types import DSP_TYPES, BSN_TYPES
from .reports import Report
from .errors import check_err_code
from ._utils import dict_to_html, request_get


List_or_str = Union[List[str], str]


def _set_params(params: Dict[str,Union[str,int]], crp_cd: str = None, start_dt: str = None, end_dt: str = None,
                fin_rpt: bool = False, dsp_tp: List_or_str = None, bsn_tp: List_or_str = None,
                sort: str = 'date', series: str = 'desc') -> Dict[str,Union[str,int]]:
    if crp_cd:
        params['crp_cd'] = crp_cd

    check_date = re.compile(r'([0-9]{4})([0-1][0-9])([0-3][0-9])')

    if start_dt:
        if check_date.search(start_dt):
            params['start_dt'] = start_dt
        else:
            raise ValueError('Invalid date format.')

    if end_dt:
        if check_date.search(end_dt):
            params['end_dt'] = end_dt
        else:
            raise ValueError('Invalid date format.')

    params['fin_rpt'] = 'N' if fin_rpt is False else 'Y'

    params.update(_get_tp_params('dsp_tp', dsp_tp))
    params.update(_get_tp_params('bsn_tp', bsn_tp))

    if sort:
        if sort in ['date', 'crp', 'rpt']:
            params['sort'] = sort
        else:
            raise ValueError('Invalid sort type.')

    if series:
        if series in ['asc', 'desc']:
            params['series'] = series
        else:
            raise ValueError('Invalid series type.')
    return params


def _get_tp_params(types, tp_data):
    params = dict()
    tp_dict = {'dsp_tp': DSP_TYPES, 'bsn_tp': BSN_TYPES}
    tp_list = tp_dict.get(types)

    if (tp_data is None) or (tp_list is None):
        return params
    elif isinstance(tp_data, str) and tp_data.upper() in tp_list:
        params[types] = tp_data.upper()
        return params
    elif isinstance(tp_data, list):
        params[types] = []
        for d in tp_data:
            dd = d.upper()
            if dd in tp_list:
                params[types].append(dd)
        if len(params[types]) == 0:
            del params[types]
        return params
    return params


class SearchResults(object):
    """ DART 검색결과 정보를 저장하는 클래스"""
    def __init__(self, **kwargs):

        self._page_no = None
        self._page_set = None
        self._total_count = None
        self._total_page = None
        self._report_list = None
        self._params = None
        self._set_data(**kwargs)

    def _set_data(self, **kwargs):
        data = kwargs.get('data')
        check_err_code(**data)
        self._page_no = data['page_no']
        self._page_set = data['page_set']
        self._total_count = data['total_count']
        self._total_page = data['total_page']
        self._report_list = [Report(**r) for r in data['report_list']]
        self._params = kwargs.get('params')

    def _search_report(self, **params):
        res = search_report(**params, return_dict=True)
        self._set_data(**res)

    @property
    def page_no(self) -> int:
        """int: 검색 페이지 번호"""
        return self._page_no

    @page_no.setter
    def page_no(self, page_no):
        params = self._params
        if isinstance(page_no, int) and 1 <= page_no <= self.total_page:
            params['page_no'] = page_no
            self._search_report(**params)
        else:
            raise ValueError('Invalid page_no')

    def next_page(self):
        self.page_no = self.page_no + 1

    def prev_page(self):
        self.page_no = self.page_no - 1

    @property
    def page_set(self) -> int:
        """int: 페이지당 건수"""
        return self._page_set

    @page_set.setter
    def page_set(self, page_set):
        params = self._params
        if isinstance(page_set, int) and (1 <= page_set <= 100):
            params['page_set'] = page_set
            self._search_report(**params)
        else:
            raise ValueError('Invalid page_no')

    @property
    def total_count(self):
        """int: 총 건수"""
        return self._total_count

    @property
    def total_page(self):
        """int: 총 페이지수"""
        return self._total_page

    @property
    def report_list(self):
        """list of Report: 검색된 리포트 리스트"""
        return self._report_list

    def filter(self, crp_cd=None, start_dt=None, end_dt=None,
               fin_rpt=False, dsp_tp=None, bsn_tp=None, sort='date',
               series='desc'):
        """ 검색 결과 필터링

        Parameters
        ----------
        crp_cd: str
            종목 코드
        start_dt: str
            검색 시작일자(YYYYMMDD)
        end_dt: str
            검색 종료일자(YYYYMMDD)
        fin_rpt: bool
            최종보고서만 검색여부, 기본값: False
        dsp_tp: list of str or str
            공시 유형(DSP_TYPES)
        bsn_tp: list of str or str
            공시 상세 유형(BSN_TYPES)
        sort: str
            정렬 방법, 접수일자(date), 회사명(crp), 보고서명(rpt), 기본값 : date
        series: str
            오름차순(asc), 내림차순(desc) 기본값 : desc

        Returns
        -------
        SearchResults
            검색결과

        """
        params = self._params

        params = _set_params(params, crp_cd=crp_cd, start_dt=start_dt, end_dt=end_dt, fin_rpt=fin_rpt,
                             dsp_tp=dsp_tp, bsn_tp=bsn_tp, sort=sort, series=series)

        return search_report(**params)

    def to_dict(self):
        """ dict 타입으로 반환

        Returns
        -------
        dict of str
            검색 결과 dict 타입로 반환

        """
        return {
            'page_no': self.page_no,
            'page_set': self.page_set,
            'total_count': self.total_count,
            'total_page': self.total_page,
            'report_list': [x.to_dict() for x in self.report_list]
        }

    def __repr__(self):
        from pprint import pformat
        return pformat(self.to_dict())

    def _repr_html_(self):
        return dict_to_html(self.to_dict(), exclude=['pages'], header=['Label', 'Data'])

    def __getitem__(self, item):
        return self._report_list[item]

    def __len__(self):
        return len(self._report_list)


SearchResults_or_dict = Union[SearchResults, Dict[str, str]]


def search_report(crp_cd: str = None, start_dt: str = None, end_dt: str = None,
                  fin_rpt: bool = False, dsp_tp: List_or_str = None, bsn_tp: List_or_str = None,
                  sort: str = 'date', series: str = 'desc', page_no: int = 1,
                  page_set: int = 10, return_dict: bool = False) -> SearchResults_or_dict:
    """ DART 공시 정보 검색

    DART 에 공시된 정보를 검색하는 함수로, Parameters 가 설정되지 않을 경우 당일 접수 10건을 검색함

    Parameters
    ----------
    crp_cd: str
        종목 코드
    start_dt: str
        검색 시작일자(YYYYMMDD)
    end_dt: str
        검색 종료일자(YYYYMMDD)
    fin_rpt: bool
        최종보고서만 검색여부, 기본값: False
    dsp_tp: list of str or str
        공시 유형(DSP_TYPES)
    bsn_tp: list of str or str
        공시 상세 유형(BSN_TYPES)
    sort: str
        정렬 방법, 접수일자(date), 회사명(crp), 보고서명(rpt), 기본값 : date
    series: str
        오름차순(asc), 내림차순(desc) 기본값 : desc
    page_no: int
        페이지 번호, 기본값: 1
    page_set: int
        페이지당 건수(1-100) 기본값: 10, 최대값: 100
    return_dict: bool
        dict 타입으로 반환할지 여부, 기본은 SearchResults

    Returns
    -------
    SearchResults or dict of str
        검색결과

    """

    api_key = DartAuth().api_key

    url = 'http://dart.fss.or.kr/api/search.json'
    params = dict()
    params['auth'] = api_key

    params = _set_params(params, crp_cd=crp_cd, start_dt=start_dt, end_dt=end_dt, fin_rpt=fin_rpt,
                         dsp_tp=dsp_tp, bsn_tp=bsn_tp, sort=sort, series=series)

    if isinstance(page_no, int) and 1 <= page_no:
        params['page_no'] = page_no

    if isinstance(page_set, int) and (1 <= page_set <= 100):
        params['page_set'] = page_set

    resp = request_get(url=url, params=params)
    data = resp.json()
    data['report_list'] = data.pop('list')

    params.pop('auth')
    if return_dict:
        return {'params': params, 'data': data}
    return SearchResults(params=params, data=data)


# 최대 캐싱 시간(분)
MAX_CACHED_MINUTES = 30
# 최대 캐싱 검색 결과 리포트 수
MAX_CACHED_SEARCH_RESULTS = 4
cached_reports = OrderedDict()


def search_report_with_cache(**kwargs):
    """ DART 공시 정보 검색 - 캐쉬 사용

    DART 에 공시된 정보를 검색하는 함수로, Parameters 가 설정되지 않을 경우 당일 접수 10건을 검색함.
    MAX_CACHED_MINUTES, MAX_CACHED_REPORT에 따라 캐쉬 저장

    Parameters
    ----------
    crp_cd: str
        종목 코드
    start_dt: str
        검색 시작일자(YYYYMMDD)
    end_dt: str
        검색 종료일자(YYYYMMDD)
    fin_rpt: bool
        최종보고서만 검색여부, 기본값: False
    dsp_tp: list of str or str
        공시 유형(DSP_TYPES)
    bsn_tp: list of str or str
        공시 상세 유형(BSN_TYPES)
    sort: str
        정렬 방법, 접수일자(date), 회사명(crp), 보고서명(rpt), 기본값 : date
    series: str
        오름차순(asc), 내림차순(desc) 기본값 : desc
    page_no: int
        페이지 번호, 기본값: 1
    page_set: int
        페이지당 건수(1-100) 기본값: 10, 최대값: 100
    return_dict: bool
        dict 타입으로 반환할지 여부, 기본은 SearchResults

    Returns
    -------
    SearchResults or dict of str
        검색결과

    """
    global cached_reports
    crp_cd = kwargs.get('crp_cd', None)
    start_dt = kwargs.get('start_dt', None)
    end_dt = kwargs.get('end_dt', None)
    fin_rpt = kwargs.get('fin_rpt', None)
    dsp_tp = tuple(kwargs.get('dsp_tp', []))
    bsn_tp = tuple(kwargs.get('bsn_tp', []))
    sort = kwargs.get('sort', None)
    series = kwargs.get('series', None)
    page_no = kwargs.get('page_no', None)
    page_set = kwargs.get('page_set', None)
    key = (crp_cd, start_dt, end_dt, fin_rpt, dsp_tp, bsn_tp, sort, series, page_no, page_set)
    cashed_time, report = cached_reports.get(key, (None, None))
    if report is None:
        report = search_report(**kwargs)
        if len(cached_reports) >= MAX_CACHED_SEARCH_RESULTS:
            cached_reports.popitem(last=False)
        cached_reports[key] = (datetime.now(), report)
    else:
        diff = int((datetime.now() - cashed_time).total_seconds() / 60)
        if diff > MAX_CACHED_MINUTES:
            report = search_report(**kwargs)
            cached_reports[key] = (datetime.now(), report)
    return report



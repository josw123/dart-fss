# -*- coding: utf-8 -*-
from typing import Union, List, Dict
#from bs4 import BeautifulSoup

from dart_fss.utils import dict_to_html
from dart_fss.api.filings import get_corp_info

str_or_list = Union[str, List[str]]


class Corp(object):
    """ 회사(종목) 정보를 담고 있는 클래스

    종목 코드, 이름, 종목 분류 및 취급 물품에 관한 기본정보를 가지고 있으며
    DART 에서 제공하는 기업개황 정보를 담고 있다.

    Attributes
    ----------
    corp_code: str
        종목 코드
    corp_name: str
        종목 이름
    stock_code: str
        주식 종목 코드
    modify_date: str
        최종 업데이트 일자

    """
    def __init__(self,
                 corp_code: str,
                 corp_name: str = None,
                 modify_date: str = None,
                 stock_code: str = None,
                 profile: bool = False):
        """ 종목 정보 초기화

        Parameters
        ----------
        corp_code: str
            종목 코드
        corp_name: str
            종목 이름
        stock_code: str
            주식 종목 코드
        modify_date: str
            최종 업데이트 일자
        profile: bool
            기업 개황 로딩 여부
        """
        # 기업 기본 정보
        self._info = {
            'corp_code': corp_code,
            'corp_name': corp_name,
            'stock_code': stock_code,
            'modify_date': modify_date,
        }
        # 데이터 로딩 여부
        self._loading = False
        # 기업 개황 로딩 여부
        self._profile = profile

    def __getattr__(self, item):
        if item in self._info:
            return self._info[item]
        else:
            # 기업 개황 로딩 설정시
            if self._profile is True:
                self.load()
            if item in self._info:
                return self._info[item]
            else:
                error = "'{}' object has no attribute '{}'".format(type(self).__name__, item)
                raise AttributeError(error)

    def load(self):
        """ 종목 정보 로딩 """
        if self._loading is False:
            info = get_corp_info(self._info['corp_code'])
            info.pop('status')
            info.pop('message')
            self._info.update(info)
            self._loading = True
        return self._info

    @property
    def info(self) -> Dict[str, str]:
        """ dict of str: 종목 정보 반환 """
        if self._profile is True:
            self.load()
        return self._info

    def to_dict(self) -> Dict[str, str]:
        """ 종목에 관한 모든 정보를 Dictionary 형태로 반환

        Returns
        -------
        dict of str
            종목에 관한 모든 정보 반환

        """
        return self.info

    def __repr__(self) -> str:
        return '[{}]{}'.format(self.corp_code, self.corp_name)

    def _repr_html_(self) -> str:
        return dict_to_html(self.to_dict(), header=['Label', 'Data'])
    #
    # def search_report(self, start_dt: str = None, end_dt: str = None, fin_rpt: bool = False,
    #                   dsp_tp: str_or_list = None, bsn_tp: str_or_list = None, sort: str = 'date',
    #                   series: str = 'desc', page_no: int = 1, page_set: int = 10) -> SearchResults:
    #     """ 종목에 관한 DART 공시 정보 검색
    #
    #     Parameters
    #     ----------
    #     start_dt: str
    #         검색 시작일자(YYYYMMDD)
    #     end_dt: str
    #         검색 종료일자(YYYYMMDD)
    #     fin_rpt: bool
    #         최종보고서만 검색여부, 기본값: False
    #     dsp_tp: str
    #         공시 유형(DSP_TYPES)
    #     bsn_tp: str or list of str
    #         공시 상세 유형(BSN_TYPES)
    #     sort: str
    #         정렬 방법, 접수일자(date), 회사명(crp), 보고서명(rpt), 기본값 : date
    #     series: str
    #         오름차순(asc), 내림차순(desc) 기본값 : desc
    #     page_no: int
    #         페이지 번호, 기본값: 1
    #     page_set: int
    #         페이지당 건수(1-100) 기본값: 10, 최대값: 100
    #
    #     Returns
    #     -------
    #     SearchResults
    #         검색결과
    #
    #     """
    #
    #     return search_report(self.crp_cd, start_dt, end_dt, fin_rpt, dsp_tp,
    #                          bsn_tp, sort, series, page_no, page_set)
    #
    # def get_financial_statement(self, start_dt: str, end_dt: str = None, fs_tp: tuple = ('fs', 'is', 'ci', 'cf'),
    #                             separate: bool = False, report_tp: str = 'annual',
    #                             lang: str = 'ko', separator: bool = True) -> FinancialStatement:
    #     """ 재무제표 검색 및 추출
    #
    #     Parameters
    #     ----------
    #     start_dt: str
    #         검색 시작일자(YYYYMMDD)
    #     end_dt: str
    #         검색 종료일자(YYYYMMDD)
    #     fs_tp: tuple
    #         'fs' 재무상태표, 'is' 손익계산서, 'ci' 포괄손익계산서, 'cf' 현금흐름표
    #     separate: bool
    #         개별지업 여뷰
    #     report_tp: str
    #         'annual' 1년, 'half' 반기, 'quarter' 분기
    #     lang: str
    #         'ko' 한글, 'en' 영문
    #     separator: bool
    #         1000단위 구분자 표시 여부
    #
    #     Returns
    #     -------
    #     FinancialStatement
    #         제무제표 검색 결과
    #
    #     """
    #     return search_financial_statement(self.crp_cd, start_dt, end_dt=end_dt, fs_tp=fs_tp, separate=separate,
    #                                       report_tp=report_tp, lang=lang, separator=separator)

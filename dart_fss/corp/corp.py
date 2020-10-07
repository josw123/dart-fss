# -*- coding: utf-8 -*-
import pandas as pd

from typing import Union, List, Dict, Tuple
from dart_fss.utils import dict_to_html, dataframe_astype
from dart_fss.api.filings import get_corp_info
from dart_fss.api.shareholder import get_executive_shareholder, get_major_shareholder
from dart_fss.filings import search as se
from dart_fss.fs import extract, FinancialStatement

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

    def __repr__(self) -> str:
        return '[{}]{}'.format(self.corp_code, self.corp_name)

    def _repr_html_(self) -> str:
        return dict_to_html(self.to_dict(), header=['Label', 'Data'])

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

    def update(self, info) -> Dict[str, str]:
        """ Update information"""
        self._info.update(info)
        return self._info

    def to_dict(self) -> Dict[str, str]:
        """ 종목에 관한 모든 정보를 Dictionary 형태로 반환

        Returns
        -------
        dict of str
            종목에 관한 모든 정보 반환

        """
        return self.info

    def get_executive_shareholder(self):
        resp = get_executive_shareholder(corp_code=self.corp_code)
        df = pd.DataFrame.from_dict(resp['list'])

        columns_astype = [
            ('sp_stock_lmp_cnt',int),
            ('sp_stock_lmp_irds_cnt', int),
            ('sp_stock_lmp_irds_rate',float),
            ('sp_stock_lmp_rate', float)
        ]
        df = dataframe_astype(df, columns_astype)
        return df

    def get_major_shareholder(self):
        resp = get_major_shareholder(corp_code=self.corp_code)
        df = pd.DataFrame.from_dict(resp['list'])
        columns_astype = [
            ('stkqy', int),
            ('stkqy_irds', int),
            ('stkrt', float),
            ('stkrt_irds', float),
            ('ctr_stkqy', int),
            ('ctr_stkrt', float)
        ]
        df = dataframe_astype(df, columns_astype)
        return df

    def search_filings(self,
                       bgn_de: str = None,
                       end_de: str = None,
                       last_reprt_at: str = 'N',
                       pblntf_ty: Union[str, List[str], None] = None,
                       pblntf_detail_ty: Union[str, List[str], None] = None,
                       corp_cls: str = None,
                       sort: str = 'date',
                       sort_mth: str = 'desc',
                       page_no: int = 1,
                       page_count: int = 10):
        """공시보고서 검색

        Parameters
        ----------
        bgn_de: str, optional
            검색시작 접수일자(YYYYMMDD), 없으면 종료일(end_de)
        end_de: str, optional
            검색종료 접수일자(YYYYMMDD), 없으면 당일
        last_reprt_at: str, optional
            최종보고서만 검색여부(Y or N), default : N
        pblntf_ty: str, optional
            공시유형
        pblntf_detail_ty: str, optional
            공시상세유형
        corp_cls: str, optional
            법인구분 : Y(유가), K(코스닥), N(코넥스), E(기타), 없으면 전체조회
        sort: str, optional
            정렬방법: '접수일자' date, '회사명' crp, '보고서명' rpt
        sort_mth: str, optional
            '오름차순' asc, '내림차순' desc, default : desc
        page_no: int, optional
            페이지 번호(1~n) default : 1
        page_count: int, optional
            페이지당 건수(1~100) 기본값 : 10, default : 100

        Returns
        -------
        SearchResults
            검색결과
        """
        return se(self.corp_code,
                  bgn_de=bgn_de,
                  end_de=end_de,
                  last_reprt_at=last_reprt_at,
                  pblntf_ty=pblntf_ty,
                  pblntf_detail_ty=pblntf_detail_ty,
                  corp_cls=corp_cls,
                  sort=sort,
                  sort_mth=sort_mth,
                  page_no=page_no,
                  page_count=page_count)

    def extract_fs(self,
                   bgn_de: str,
                   end_de: str = None,
                   fs_tp: Tuple[str] = ('bs', 'is', 'cis', 'cf'),
                   separate: bool = False,
                   report_tp: str = 'annual',
                   lang: str = 'ko',
                   separator: bool = True,
                   dataset: str = 'xbrl') -> FinancialStatement:
        """
         재무제표 검색

         Parameters
         ----------
         bgn_de: str
             검색 시작일자(YYYYMMDD)
         end_de: str, optional
             검색 종료일자(YYYYMMDD)
         fs_tp: tuple of str, optional
             'bs' 재무상태표, 'is' 손익계산서, 'cis' 포괄손익계산서, 'cf' 현금흐름표
         separate: bool, optional
             개별재무제표 여부
         report_tp: str, optional
             'annual' 1년, 'half' 반기, 'quarter' 분기
         lang: str, optional
             'ko' 한글, 'en' 영문
         separator: bool, optional
             1000단위 구분자 표시 여부
         dataset: str, optional
            'xbrl': xbrl 파일 우선 데이터 추출, 'web': web page 우선 데이터 추출(default: 'xbrl')
         Returns
         -------
         FinancialStatement
             제무제표 검색 결과

         """
        return extract(self.corp_code, bgn_de, end_de, fs_tp, separate, report_tp, lang, separator, dataset)

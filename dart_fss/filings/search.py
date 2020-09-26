# -*- coding: utf-8 -*-
from typing import Union, List
from dart_fss.api.filings import search_filings
from dart_fss.filings.search_result import SearchResults
str_or_list = Union[str, List[str]]


def search(corp_code: str = None,
           bgn_de: str = None,
           end_de: str = None,
           last_reprt_at: str = 'N',
           pblntf_ty: str_or_list = None,
           pblntf_detail_ty: str_or_list = None,
           corp_cls: str = None,
           sort: str = 'date',
           sort_mth: str = 'desc', # 현재 sort_mth 설정시 오류 발생
           page_no: int = 1,
           page_count: int = 10):
    """공시보고서 검색

    Parameters
    ----------
    corp_code: str, optional
        공시대상회사의 고유번호(8자리), 고유번호(corp_code)가 없는 경우 검색기간은 3개월로 제한
    bgn_de: str, optional
        검색시작 접수일자(YYYYMMDD), 없으면 종료일(end_de)
    end_de: str, optional
        검색종료 접수일자(YYYYMMDD), 없으면 당일
    last_reprt_at: str, optional
        최종보고서만 검색여부(Y or N), default : N
    pblntf_ty: str, optional
        공시유형 / Open DART  공시정보 -> 공시검색 -> 상세유형 참고
    pblntf_detail_ty: str, optional
        공시상세유형 / Open DART  공시정보 -> 공시검색 -> 상세유형 참고
    corp_cls: str, optional
        법인구분 : Y(유가), K(코스닥), N(코넥스), E(기타), 없으면 전체조회
    sort: str, optional
        정렬, {접수일자: date, 회사명: crp, 고서명: rpt}
    sort_mth: str, optional
        오름차순(asc), 내림차순(desc), default : desc
    page_no: int, optional
        페이지 번호(1~n) default : 1
    page_count: int, optional
        페이지당 건수(1~100) 기본값 : 10, default : 100

    Returns
    -------
    SearchResults
        검색결과
    """
    resp = search_filings(corp_code=corp_code,
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
    return SearchResults(resp)
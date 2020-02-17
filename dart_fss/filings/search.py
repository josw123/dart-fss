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
           sort: str = 'date',
           sort_mth: str = None, # 현재 sort_mth 설정시 오류 발생
           page_no: int = 1,
           page_count: int = 10):

    payload = {
        'corp_code': corp_code,
        'bgn_de': bgn_de,
        'end_de': end_de,
        'last_reprt_at': last_reprt_at,
        'pblntf_ty': pblntf_ty,
        'pblntf_detail_ty': pblntf_detail_ty,
        'sort': sort,
        'sort_mth': sort_mth,
        'page_no': page_no,
        'page_count': page_count
    }

    resp = search_filings(corp_code=corp_code,
                          bgn_de=bgn_de,
                          end_de=end_de,
                          last_reprt_at=last_reprt_at,
                          pblntf_ty=pblntf_ty,
                          pblntf_detail_ty=pblntf_detail_ty,
                          sort=sort,
                          sort_mth=sort_mth,
                          page_no=page_no,
                          page_count=page_count)
    return SearchResults(resp)
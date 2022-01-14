# -*- coding: utf-8 -*-
from typing import Dict
from ..helper import api_request


def xbrl_taxonomy(
    sj_div: str,
    api_key: str = None
) -> Dict:
    """ 금융감독원 회계포탈에서 제공하는 IFRS 기반 XBRL 재무제표 공시용 표준계정과목체계(계정과목) 을 제공합니다.

    Parameters
    ----------
    sj_div: str
        (※재무제표구분 참조)
    api_key: str, optional
        DART_API_KEY, 만약 환경설정 DART_API_KEY를 설정한 경우 제공하지 않아도 됨
    Returns
    -------
    dict
        XBRL택사노미재무제표양식
    """

    path = '/api/xbrlTaxonomy.json'

    return api_request(
        api_key=api_key,
        path=path,
        sj_div=sj_div,
    )

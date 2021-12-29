# -*- coding: utf-8 -*-
from typing import Dict
from ..helper import api_request


def majorstock(
    corp_code: str, 
    api_key: str = None
) -> Dict:
    """ 주식등의 대량보유상황보고서 내에 대량보유 상황보고 정보를 제공합니다.

    Parameters
    ----------
    corp_code: str
        공시대상회사의 고유번호(8자리)※ 개발가이드 > 공시정보 > 고유번호 참고
    api_key: str, optional
        DART_API_KEY, 만약 환경설정 DART_API_KEY를 설정한 경우 제공하지 않아도 됨
    Returns
    -------
    dict
        대량보유 상황보고
    """

    path = '/api/majorstock.json'

    return api_request(
        api_key=api_key,
        path=path, 
        corp_code=corp_code, 
    )
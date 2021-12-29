# -*- coding: utf-8 -*-
from typing import Dict
from ..helper import api_request


def fnltt_multi_acnt(
    corp_code: str, 
    bsns_year: str, 
    reprt_code: str, 
    api_key: str = None
) -> Dict:
    """ 상장법인(금융업 제외)이 제출한 정기보고서 내에 XBRL재무제표의 주요계정과목(재무상태표, 손익계산서)을 제공합니다.
(상장법인 복수조회 가능)

    Parameters
    ----------
    corp_code: str
        공시대상회사의 고유번호(8자리)※ 개발가이드 > 공시정보 > 고유번호 참고
    bsns_year: str
        사업연도(4자리) ※ 2015년 이후 부터 정보제공
    reprt_code: str
        1분기보고서 : 11013반기보고서 : 110123분기보고서 : 11014사업보고서 : 11011
    api_key: str, optional
        DART_API_KEY, 만약 환경설정 DART_API_KEY를 설정한 경우 제공하지 않아도 됨
    Returns
    -------
    dict
        다중회사 주요계정
    """

    path = '/api/fnlttMultiAcnt.json'

    return api_request(
        api_key=api_key,
        path=path, 
        corp_code=corp_code,  
        bsns_year=bsns_year,  
        reprt_code=reprt_code, 
    )
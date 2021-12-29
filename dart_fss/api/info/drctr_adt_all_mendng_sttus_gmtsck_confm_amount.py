# -*- coding: utf-8 -*-
from typing import Dict
from ..helper import api_request


def drctr_adt_all_mendng_sttus_gmtsck_confm_amount(
    corp_code: str, 
    bsns_year: str, 
    reprt_code: str, 
    api_key: str = None
) -> Dict:
    """ 정기보고서(사업, 분기, 반기보고서) 내에 이사·감사 전체의 보수현황(주주총회 승인금액)을 제공합니다.

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
        이사·감사 전체의 보수현황(주주총회 승인금액)
    """

    path = '/api/drctrAdtAllMendngSttusGmtsckConfmAmount.json'

    return api_request(
        api_key=api_key,
        path=path, 
        corp_code=corp_code,  
        bsns_year=bsns_year,  
        reprt_code=reprt_code, 
    )
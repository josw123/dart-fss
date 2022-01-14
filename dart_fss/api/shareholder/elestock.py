# -*- coding: utf-8 -*-
from typing import Dict
from ..helper import api_request


def elestock(
    corp_code: str,
    api_key: str = None
) -> Dict:
    """ 임원ㆍ주요주주특정증권등 소유상황보고서 내에 임원ㆍ주요주주 소유보고 

정보를 제공합니다.

    Parameters
    ----------
    corp_code: str
        공시대상회사의 고유번호(8자리)※ 개발가이드 > 공시정보 > 고유번호 참고
    api_key: str, optional
        DART_API_KEY, 만약 환경설정 DART_API_KEY를 설정한 경우 제공하지 않아도 됨
    Returns
    -------
    dict
        임원ㆍ주요주주 소유보고
    """

    path = '/api/elestock.json'

    return api_request(
        api_key=api_key,
        path=path,
        corp_code=corp_code,
    )

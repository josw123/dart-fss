# -*- coding: utf-8 -*-
from ..helper import api_request


def get_corp_info(corp_code: str):
    """ 기업 개황 조회

    Parameters
    ----------
    corp_code: str
        공시대상회사의 고유번호(8자리)

    Returns
    -------
    dict
        기업 개황
    """
    path = '/api/company.json'

    return api_request(path=path, corp_code=corp_code)

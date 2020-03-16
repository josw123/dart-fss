import re

from urllib.parse import urljoin

from dart_fss.auth import get_api_key
from dart_fss.utils import request
from dart_fss.errors import check_status
from dart_fss.api.helper import corp_code_checker, bsns_year_checker, reptr_code_checker


fs_div_checker = re.compile(r'CFS|OFS', re.IGNORECASE)


def get_single_fs(corp_code: str, bsns_year: str, reprt_code: str, fs_div: str):
    """ 단일회사 전체 재무제표 조회

    Parameters
    ----------
    corp_code: str
        공시대상회사의 고유번호(8자리)
    bsns_year: str
        사업연도(4자리)
    reprt_code: str
        1분기보고서 : 11013, 반기보고서 : 110123, 3분기보고서 : 11014, 사업보고서 : 11011
    fs_div: str
        CFS:연결재무제표, OFS:재무제표

    Returns
    -------
    dict
        단일회사 전체 재무제표
    """

    if corp_code_checker.search(corp_code) is None:
        raise ValueError('corp_code must be 8 digits')

    if bsns_year_checker.search(bsns_year) is None:
        raise ValueError('bsns_year must be 4 digits')

    if reptr_code_checker.search(reprt_code) is None:
        raise ValueError('invalid reprt_code')

    if fs_div_checker.search(fs_div) is None:
        raise ValueError('fs_div must be CFS or OFS')

    fs_div = fs_div.upper()

    # Open DART Base URL
    base = 'https://opendart.fss.or.kr/'

    path = '/api/fnlttSinglAcntAll.json'

    # Request URL
    url = urljoin(base, path)

    # Get DART_API_KEY
    api_key = get_api_key()

    # Set payload
    payload = {
        'crtfc_key': api_key,
        'corp_code': corp_code,
        'bsns_year': bsns_year,
        'reprt_code': reprt_code,
        'fs_div': fs_div,
    }

    # Request Data
    resp = request.get(url=url, payload=payload)

    # Convert Response to json
    dataset = resp.json()

    # Status Code Check
    check_status(**dataset)
    return dataset

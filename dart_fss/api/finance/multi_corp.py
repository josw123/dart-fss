from typing import Union, List

from urllib.parse import urljoin
from dart_fss.auth import get_api_key
from dart_fss.utils import request
from dart_fss.errors import check_status
from ..helper import bsns_year_checker, reptr_code_checker


def get_multi_corp(corp_code: Union[str, List[str]], bsns_year: str, reprt_code: str):
    """ 다중회사 주요계정 조회

    Parameters
    ----------
    corp_code: str or list of str
        공시대상회사의 고유번호(8자리) ex) ['00356370','00334624']
    bsns_year: str
        사업연도(4자리)
    reprt_code: str
        1분기보고서 : 11013, 반기보고서 : 110123, 3분기보고서 : 11014, 사업보고서 : 11011

    Returns
    -------
    dict
        다중회사 주요계정 조회 결과
    """
    if reprt_code and reptr_code_checker.search(reprt_code) is None:
        raise ValueError('invalid reprt_code')

    if bsns_year and bsns_year_checker.search(bsns_year) is None:
        raise ValueError('bsns_year must be 4 digits')

    # Open DART Base URL
    base = 'https://opendart.fss.or.kr/'

    # Path
    path = '/api/fnlttMultiAcnt.json'
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
    }

    # Request Data
    resp = request.get(url=url, payload=payload)

    # Convert Response to json
    dataset = resp.json()

    # Status Code Check
    check_status(**dataset)

    return dataset

from dart_fss.auth import get_api_key
from dart_fss.utils import request
from dart_fss.errors import check_status


def get_multi_corp(corp_code: str, bsns_year: str, reprt_code: str):
    """ 다중회사 주요계정 조회

    Parameters
    ----------
    corp_code: str
        공시대상회사의 고유번호(8자리)
    bsns_year: str
        사업연도(4자리)
    reprt_code: str
        1분기보고서 : 11013, 반기보고서 : 110123, 3분기보고서 : 11014, 사업보고서 : 11011

    Returns
    -------
    dict
        다중회사 주요계정 조회 결과
    """
    url = 'https://opendart.fss.or.kr/api/fnlttMultiAcnt.json'
    api_key = get_api_key()
    payload = {
        'crtfc_key': api_key,
        'corp_code': corp_code,
        'bsns_year': bsns_year,
        'reprt_code': reprt_code,
    }

    resp = request.get(url=url, payload=payload)

    dataset = resp.json()

    # Check Error
    check_status(**dataset)
    return dataset

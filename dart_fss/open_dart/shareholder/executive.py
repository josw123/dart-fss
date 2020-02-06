from dart_fss.auth import get_api_key
from dart_fss.utils import request
from dart_fss.errors import check_status


def get_executive_shareholder(corp_code: str):
    """ 임원ㆍ주요주주 소유보고

    Parameters
    ----------
    corp_code: str
        공시대상회사의 고유번호(8자리)

    Returns
    -------
    dict
        임원ㆍ주요주주 소유보고
    """
    url = 'https://opendart.fss.or.kr/api/elestock.json'
    api_key = get_api_key()
    payload = {
        'crtfc_key': api_key,
        'corp_code': corp_code,
    }

    resp = request.get(url=url, payload=payload)

    dataset = resp.json()

    # Check Error
    check_status(**dataset)
    return dataset

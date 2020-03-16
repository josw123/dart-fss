from urllib.parse import urljoin

from dart_fss.auth import get_api_key
from dart_fss.utils import request
from dart_fss.errors import check_status


def get_taxonomy(sj_div: str):
    """ XBRL 택사노미재무제표양식 조회

    Parameters
    ----------
    sj_div: str
        재무제표구분 (https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2020001)

    Returns
    -------
    dict
        XBRL 텍사노미
    """
    # Open DART Base URL
    base = 'https://opendart.fss.or.kr/'

    path = '/api/xbrlTaxonomy.json'

    # Request URL
    url = urljoin(base, path)

    # Get DART_API_KEY
    api_key = get_api_key()

    # Set payload
    payload = {
        'crtfc_key': api_key,
        'sj_div': sj_div,
    }

    # Request Data
    resp = request.get(url=url, payload=payload)

    # Convert Response to json
    dataset = resp.json()

    # Status Code Check
    check_status(**dataset)
    return dataset

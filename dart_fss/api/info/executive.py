from ..helper import api_request


def get_executive(corp_code: str, bsns_year: str, reprt_code: str):
    """ 임원현황

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
        임원현황
    """

    path = '/api/exctvSttus.json'
    return api_request(path=path, corp_code=corp_code, bsns_year=bsns_year, reprt_code=reprt_code)

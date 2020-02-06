from ..helper import api_request


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
    path = '/api/elestock.json'
    return api_request(path=path, corp_code=corp_code)

from ..helper import api_request


def get_major_shareholder(corp_code: str):
    """ 대량보유 상황보고

    Parameters
    ----------
    corp_code: str
        공시대상회사의 고유번호(8자리)

    Returns
    -------
    dict
        대량보유 상황보고
    """
    path = '/api/majorstock.json'
    return api_request(path=path, corp_code=corp_code)
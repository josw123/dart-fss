# -*- coding: utf-8 -*-
from dart_fss.utils import request
from bs4 import BeautifulSoup


def get_trading_halt_list(corp_cls: str, include_corp_name=True) -> dict:
    """ 상장 회사 dictionary 반환

    Parameters
    ----------
    corp_cls: str
        Y: stock market(코스피), K: kosdaq market(코스닥), N: konex Market(코넥스)
    include_corp_name: bool, optional
        if True, returning dictionary includes corp_name(default: True)
    Returns
    -------
    dict of {stock_code: information}
        trading halt list
    """

    if corp_cls.upper() == 'E':
        raise ValueError('ETC market is not supported')

    corp_cls_to_market = {
        "Y": 1,
        "K": 2,
        "N": 6,
    }

    url = 'https://kind.krx.co.kr/investwarn/tradinghaltissue.do'
    referer = 'https://kind.krx.co.kr/investwarn/tradinghaltissue.do?method=searchTradingHaltIssueMain'

    market_type = corp_cls_to_market[corp_cls.upper()]
    payload = {
        'method': 'searchTradingHaltIssueSub',
        'currentPageSize': 3000,
        'pageIndex': 1,
        'searchMode': '',
        'searchCodeType': '',
        'searchCorpName': '',
        'forward': 'tradinghaltissue_down',
        'paxreq': '',
        'outsvcno': '',
        'marketType': market_type,
        'repIsuSrtCd': '',
    }

    trading_halt_list = dict()

    resp = request.post(url=url, payload=payload, referer=referer)
    html = BeautifulSoup(resp.text, 'html.parser')
    rows = html.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 0:
            corp_name = cols[1].text.strip()
            stock_code = cols[2].text.strip()
            issue = cols[3].text.strip()

            corp_info = {'issue': issue, 'corp_cls': corp_cls}
            if include_corp_name:
                corp_info['corp_name'] = corp_name
            trading_halt_list[stock_code] = corp_info

    return trading_halt_list

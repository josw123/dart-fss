# -*- coding: utf-8 -*-
from dart_fss.utils import request
from bs4 import BeautifulSoup


def get_stock_market_list(corp_cls: str, include_corp_name=True) -> dict:
    """ 상장 회사 dictionary 반환

    Parameters
    ----------
    corp_cls: str
        Y: stock market(코스피), K: kosdaq market(코스피), N: konex Market(코넥스)
    include_corp_name: bool, optional
        if True, returning dictionary includes corp_name(default: True)
    Returns
    -------
    dict of {stock_code: information}
        상장 회사 정보 dictionary 반환( 회사 이름, 섹터, 물품)
    """

    if corp_cls.upper() == 'E':
        raise ValueError('ETC market is not supported')

    corp_cls_to_market = {
        "Y": "stockMkt",
        "K": "kosdaqMkt",
        "N": "konexMkt",
    }

    url = 'http://kind.krx.co.kr/corpgeneral/corpList.do'
    referer = 'http://kind.krx.co.kr/corpgeneral/corpList.do?method=loadInitPage'

    market_type = corp_cls_to_market[corp_cls.upper()]
    payload = {
        'method': 'download',
        'pageIndex': 1,
        'currentPageSize': 5000,
        'orderMode': 3,
        'orderStat': 'D',
        'searchType': 13,
        'marketType': market_type,
        'fiscalYearEnd': 'all',
        'location': 'all',
    }

    stock_market_list = dict()

    resp = request.post(url=url, payload=payload, referer=referer)
    html = BeautifulSoup(resp.text, 'html.parser')
    rows = html.find_all('tr')

    for row in rows:
        cols = row.find_all('td')
        if len(cols) > 0:
            corp_name = cols[0].text.strip()
            stock_code = cols[1].text.strip()
            sector = cols[2].text.strip()
            product = cols[3].text.strip()
            corp_info = {'sector': sector, 'product': product, 'corp_cls': corp_cls}
            if include_corp_name:
                corp_info['corp_name'] = corp_name
            stock_market_list[stock_code] = corp_info

    return stock_market_list

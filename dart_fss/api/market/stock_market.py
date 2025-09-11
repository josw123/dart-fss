# -*- coding: utf-8 -*-
import warnings
from typing import Dict
from dart_fss.utils import request
from bs4 import BeautifulSoup

def get_stock_market_list(corp_cls: str, include_corp_name: bool = True) -> Dict[str, dict]:
    """상장 회사 dictionary 반환

    Parameters
    ----------
    corp_cls: str
        'Y' (코스피), 'K' (코스닥), 'N' (코넥스)
    include_corp_name: bool, optional
        True면 회사명을 포함해 반환 (default: True)

    Returns
    -------
    Dict[str, dict]
        {주식코드: {'sector': ..., 'market_type': ..., 'product': ..., 'corp_cls': ..., 'corp_name': ...?}}
    """
    if not isinstance(corp_cls, str) or not corp_cls:
        raise ValueError("corp_cls must be one of {'Y','K','N'}")

    cls = corp_cls.upper()
    if cls == 'E':
        raise ValueError('ETC market is not supported')

    corp_cls_to_market = {
        'Y': 'stockMkt',
        'K': 'kosdaqMkt',
        'N': 'konexMkt',
    }
    if cls not in corp_cls_to_market:
        raise ValueError("Invalid corp_cls. Use 'Y' (KOSPI), 'K' (KOSDAQ), or 'N' (KONEX).")

    # 화면 표기(한글) → KRX 내부 파라미터 매핑
    market_type_info = {
        '유가': 'stockMkt',
        '코스닥': 'kosdaqMkt',
        '코넥스': 'konexMkt',
    }

    url = 'https://kind.krx.co.kr/corpgeneral/corpList.do'
    referer = 'https://kind.krx.co.kr/corpgeneral/corpList.do?method=loadInitPage'

    market_type = corp_cls_to_market[cls]
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

    # 결과 저장
    stock_market_list: Dict[str, dict] = {}

    try:
        resp = request.post(url=url, payload=payload, referer=referer)
        # lxml이 설치되어 있으면 더 빠름; 없으면 html.parser로 폴백
        parser = 'lxml'
        try:
            import lxml  # noqa: F401
        except Exception:
            parser = 'html.parser'

        soup = BeautifulSoup(resp.text, parser)

        # 표 본문만 대상으로 검색(헤더/푸터 스킵)
        tbody = soup.find('tbody')
        if tbody is None:
            # 구조 변경 가능성 대비
            rows = soup.find_all('tr')
        else:
            rows = tbody.find_all('tr')

        mkt_map = market_type_info  # 지역 변수 캐시

        for row in rows:
            cols = row.find_all('td')
            # 기대 컬럼: [회사명, 시장구분(한글), 종목코드, 업종, 제품]
            if len(cols) < 5:
                continue

            # strip + 내부 공백 정규화
            def norm(x: str) -> str:
                return ' '.join(x.strip().split())

            corp_name = norm(cols[0].get_text())
            market_kr  = norm(cols[1].get_text())
            stock_code = norm(cols[2].get_text())
            sector     = norm(cols[3].get_text())
            product    = norm(cols[4].get_text())

            # 시장 구분(한글)이 예상과 다르면 스킵 (사이트 구조/라벨 변경 대응)
            market_key = mkt_map.get(market_kr)
            if market_key is None:
                # 다른 시장(예: ETF/관리종목 등) 라벨이 섞일 수 있으므로 조용히 패스
                continue

            info = {
                'sector': sector,
                'market_type': market_key,
                'product': product,
                'corp_cls': cls,
            }
            if include_corp_name:
                info['corp_name'] = corp_name

            # 주식코드를 키로 사용
            if stock_code:
                stock_market_list[stock_code] = info

        if not stock_market_list:
            warnings.warn(
                'No rows parsed. The KRX page structure may have changed or the response was empty.',
                UserWarning
            )

    except Exception as e:
        warnings.warn(f'Failed to fetch stock market list ({cls}): {e}', UserWarning)

    return stock_market_list

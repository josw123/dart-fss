# -*- coding: utf-8 -*-
from typing import Dict
from .types import CRP_TYPES

MARKET = {key: market + 'Mkt' for key, market in CRP_TYPES.items()}


def get_market_list() -> Dict[str, str]:
    """ 마켓의 종류를 반환하는 함수

    Returns
    -------
    dict of str
        마켓의 종류

    """
    return MARKET


def get_market_name(market: str = None) -> str:
    """ 입력된 값에 대한 마켓의 종류를 반환하는 함수

    Parameters
    ----------
    market: str
        마켓에 대한 약어 혹은 마켓의 풀네임

    Returns
    -------
    str
        입력된 값에 대한 마켓 타입

    Raises
    ------
    ValueError
        입력된 값에 대한 마켓의 타입을 알 수 없을때

    """

    if market:
        for key, market_type in MARKET.items():
            if market.lower() in [key.lower(), market_type.lower(), CRP_TYPES[key].lower()]:
                return market_type
    else:
        return 'AllMkt'
    raise ValueError('Invalid market')


def get_market_type(market: str) -> str:
    """ 입력된 값에 대한 마켓의 약어를 반환하는 함수

    Parameters
    ----------
    market: str
        마켓에 대한 약어 혹은 마켓의 풀네임

    Returns
    -------
    str
        입력된 값에 대한 마켓의 약어

    Raises
    ------
    ValueError
        입력된 값에 대한 마켓의 타입을 알 수 없을때

    """
    for key, market_type in MARKET.items():
        if market.lower() in [key.lower(), market_type.lower(), CRP_TYPES[key].lower()]:
            return key

    raise ValueError('Invalid market')

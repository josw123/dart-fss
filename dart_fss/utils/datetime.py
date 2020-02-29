# -*- coding: utf-8 -*-
from typing import  Union
from datetime import datetime

str_or_datetime = Union[str, datetime]


def get_datetime(date: str_or_datetime) -> datetime:
    """ 문자열을 datetime올 변환

    Parameters
    ----------
    date: str or datetime
        datetime 문자열

    Returns
    -------
    datetime
        변환된 datetime

    """
    if isinstance(date, str):
        return datetime.strptime(date, '%Y%m%d')
    elif isinstance(date, datetime):
        return date
    else:
        raise ValueError('Invalid datetime format')


def check_datetime(date: str_or_datetime,
                   start_date: str_or_datetime = None,
                   end_date: str_or_datetime = None) -> bool:
    """ Date가 올바른지 체크하는 함수

    Parameters
    ----------
    date: str or datetime
        체크할 값
    start_date: str or datetime
        시작 일자
    end_date: str or datetime
        종료 일자

    Returns
    -------
    bool
        Date가 start_date와 end_date 사이에 있는지 여부
    """
    date = get_datetime(date)
    if start_date is not None:
        start_date = get_datetime(start_date)
        if date < start_date:
            return False
    if end_date is not None:
        end_date = get_datetime(end_date)
        if date > end_date:
            return False
    return True

# -*- coding: utf-8 -*-
import re
import requests

from typing import List, Union, Dict

from fake_useragent import UserAgent


def request_get(url: str, params: dict = None, timeout: int = 120, stream: bool = False):
    return requests.get(url=url, params=params, headers=user_agent(), timeout=timeout, stream=stream)


def compare_str(str1: str, str2: str) -> bool:
    str1 = str1.strip().lower()
    str2 = str2.strip().lower()
    return str1 == str2


CHANGE_AGENT_MINUTE = 10
cached_agent = {
    'datetime': None,
    'agent': None
}


def user_agent() -> Dict[str, str]:
    global cached_agent

    time = cached_agent.get('datetime', None)
    agent = cached_agent.get('agent', None)

    diff_time = int((datetime.now() - time).seconds / 60) if time is not None else 100

    if agent is None or (diff_time > CHANGE_AGENT_MINUTE):
        ua = UserAgent()
        agent = ua.chrome
        cached_agent['agent'] = agent
        cached_agent['datetime'] = datetime.now()

    return {'User-Agent': str(agent)}


def str_unit_to_number_unit(str_unit: str):
    str_unit = re.sub(r'\s+', '', str_unit)
    str_unit_to_unit = {
        '억원': 100000000,
        '천만원': 10000000,
        '백만원': 1000000,
        '십만원': 100000,
        '만원': 10000,
        '천원': 1000,
        '백원': 100,
        '십원': 10,
        '원': 1,
        'USD': 1
    }
    return str_unit_to_unit[str_unit]


def query_to_regex(query):
    if isinstance(query, str):
        regex = re.compile(query, re.IGNORECASE)
    elif isinstance(query, list):
        pattern = '(' + '|'.join(query) + ')'
        regex = re.compile(pattern, re.IGNORECASE)
    else:
        raise TypeError('Invalid query type')
    return regex


def strWS(word):
    return r'\s*'.join(word)


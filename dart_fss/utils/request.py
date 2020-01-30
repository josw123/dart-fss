# -*- coding: utf-8 -*-
import re
import requests
from time import sleep
from fake_useragent import UserAgent
from .cache import cache
from .singleton import Singleton


@cache()
def get_user_agent():
    ua = UserAgent()
    agent = ua.chrome
    return str(agent)


def query_to_regex(query):
    if isinstance(query, str):
        regex = re.compile(query, re.IGNORECASE)
    elif isinstance(query, list):
        pattern = '(' + '|'.join(query) + ')'
        regex = re.compile(pattern, re.IGNORECASE)
    else:
        raise TypeError('Invalid query type')
    return regex


class Request(object, metaclass=Singleton):

    def __init__(self):
        self.s = requests.Session()
        self.update_user_agent()
        self.delay = None

    def update_user_agent(self, force: bool = False):
        if force:
            ua = UserAgent()
            agent = ua.chrome
            user_agent = str(agent)
        else:
            user_agent = get_user_agent()
        self.s.headers.update({'user-agent': user_agent})

    def update_referer(self, referer: str = None):
        if referer is not None:
            self.s.headers.update({'referer': referer})

    def set_proxies(self, proxies: dict = None):
        if proxies is not None:
            import copy
            self.s.proxies = copy.deepcopy(proxies)

    def set_delay(self, second: float = None):
        self.delay = second

    def request(self,
                url: str,
                method: str = 'GET',
                payload: dict = None,
                referer: str = None,
                stream: bool = False,
                timeout: int = 120):

        headers = self.s.headers
        if referer is not None:
            headers['referer'] = referer

        # Session-level state such as cookies will not get applied to your request.
        # To get a PreparedRequest with that state applied,
        # replace the call to Request.prepare() with a call to Session.prepare_request()
        req = requests.Request(method, url=url, params=payload, headers=headers)
        prepped = self.s.prepare_request(req)
        resp = self.s.send(prepped, stream=stream, timeout=timeout)
        if self.delay is not None:
            sleep(self.delay)
        return resp

    def get(self, url: str,
            payload: dict = None,
            referer: str = None,
            stream: bool = False,
            timeout: int = 120):
        return self.request(url=url, method='GET', payload=payload, referer=referer, stream=stream, timeout=timeout)

    def post(self, url: str,
             payload: dict = None,
             referer: str = None,
             stream: bool = False,
             timeout: int = 120):
        return self.request(url=url, method='POST', payload=payload, referer=referer, stream=stream, timeout=timeout)

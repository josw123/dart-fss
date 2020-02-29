# -*- coding: utf-8 -*-
import re
import requests
from time import sleep
from fake_useragent import UserAgent
from .cache import cache
from .singleton import Singleton


@cache()
def get_user_agent():
    """ Return user-agent
    Returns
    -------
    str
        user-agent
    """
    ua = UserAgent()
    agent = ua.chrome
    return str(agent)


def query_to_regex(query):
    """ query to regular expression

    Parameters
    ----------
    query: str or list of str
        query

    Returns
    -------
    Pattern object
        regular expression
    """
    if isinstance(query, str):
        regex = re.compile(query, re.IGNORECASE)
    elif isinstance(query, list):
        pattern = '(' + '|'.join(query) + ')'
        regex = re.compile(pattern, re.IGNORECASE)
    else:
        raise TypeError('Invalid query type')
    return regex


class Request(object, metaclass=Singleton):
    """HTTP 요청을 보내는 클래스

    HTTP 요청을 위해 사용되는 클래스입니다.
    User-Agent 및 Cookies 관련 정보를 저장하고 있습니다.

    Attributes
    ---------
    s: Session
        Requests Session
    delay: float
        Delay for repeat delay, Default: 1s

    """
    def __init__(self):
        self.s = requests.Session()
        self.update_user_agent()
        self.delay = 1

    def update_user_agent(self, force: bool = False):
        """ Update User-Agent

        Parameters
        ----------
        force: bool
            Force update
        """
        if force:
            ua = UserAgent()
            agent = ua.chrome
            user_agent = str(agent)
        else:
            user_agent = get_user_agent()
        self.s.headers.update({'user-agent': user_agent})

    def set_proxies(self, proxies: dict = None):
        """ Set proxies

        Parameters
        ----------
        proxies: dict
            proxies
        """
        if proxies is not None:
            import copy
            self.s.proxies = copy.deepcopy(proxies)

    def set_delay(self, second: float = None):
        """ Set delay

        Parameters
        ----------
        second: float
            delay for repeat
        """
        self.delay = second

    def request(self,
                url: str,
                method: str = 'GET',
                payload: dict = None,
                referer: str = None,
                stream: bool = False,
                timeout: int = 120):
        """ send http requests

        Parameters
        ----------
        url: str
            URL
        method: str, optional
            GET, OPTIONS, POST, PUT, PATCH or DELETE
        payload: dict, optional
            Request parameters
        referer: str, optional
            Temporary referer
        stream: bool, optional
            Stream optional, default False
        timeout: int, optional
            default 120s

        Returns
        -------
        requests.Response
            Response
        """
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
        """ Request get method

        Parameters
        ----------
        url: str
            URL
        payload: dict, optional
            Request parameters
        referer: str, optional
            Temporary referer
        stream: bool, optional
            Stream optional, default False
        timeout: int, optional
            default 120s

        Returns
        -------
        requests.Response
            Response
        """
        return self.request(url=url, method='GET', payload=payload, referer=referer, stream=stream, timeout=timeout)

    def post(self, url: str,
             payload: dict = None,
             referer: str = None,
             stream: bool = False,
             timeout: int = 120):
        """ Request post method

        Parameters
        ----------
        url: str
            URL
        payload: dict, optional
            Request parameters
        referer: str, optional
            Temporary referer
        stream: bool, optional
            Stream optional, default False
        timeout: int, optional
            default 120s

        Returns
        -------
        requests.Response
            Response
        """
        return self.request(url=url, method='POST', payload=payload, referer=referer, stream=stream, timeout=timeout)

    def download(self,
                 url: str,
                 path: str,
                 filename: str = None,
                 method: str = 'GET',
                 payload: dict = None,
                 referer: str = None,
                 timeout: int = 120) -> dict:
        """ Download File

        Parameters
        ----------
        url: str
            Request URL
        path: str
            Download Path
        filename: str
            filename for saving
        method: str, optional
            Request Method
        payload: dict, optional
            Request parameters
        referer: str, optional
            Temporary referer
        timeout: int, optional
            default 120s

        Returns
        -------
        dict
            filename, path, full_path

        """

        from .spinner import Spinner
        from .file import create_folder
        from urllib.parse import unquote
        import os
        # Create Folder
        create_folder(path)

        r = self.request(url=url, method=method, payload=payload, referer=referer, stream=True, timeout=timeout)

        # Check validity
        headers = r.headers.get('Content-Disposition')
        if headers is None or not re.search('attachment', headers):
            raise FileNotFoundError('target does not exist')

        # total_size = int(r.headers.get('content-length', 0))
        block_size = 8192

        # Extract filename
        extracted_filename = unquote(re.findall(r'filename="?([^"]*)"?', headers)[0])

        if filename is None:
            filename = extracted_filename
        else:
            filename = filename.format(extracted_filename)

        spinner = Spinner('Downloading ' + filename)
        spinner.start()

        file_path = os.path.join(path, filename)
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=block_size):
                if chunk is not None:
                    f.write(chunk)
        r.close()
        spinner.stop()
        return {'filename': filename, 'path': path, 'full_path': file_path}


# Request object
request = Request()

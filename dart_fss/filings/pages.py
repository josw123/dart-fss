# -*- coding: utf-8 -*-

import re
import base64

from typing import Dict
from bs4 import BeautifulSoup
from dart_fss.utils import request


class Page(object):
    """ DART 공시 리포트의 페이지 클래스

    DART 공시 리포트의 개별 페이지 정보를 담고 있는 클래스.
    HTML 정보를 담고 있다.

    Attributes
    ----------
    title: str
        페이지의 타이틀
    rcp_no: str
        접수번호
    ele_id: str
        리포트에서 페이지 번호
    dcm_no: str
        페이저 관리 번호

    """

    _BASE_URL_ = 'http://dart.fss.or.kr/report/viewer.do'

    def __init__(self, title: str, rcp_no: str, dcm_no: str, ele_id: str,
                 offset: str, length: str, dtd: str, lazy_loading=True):
        self.title = title
        self.rcp_no = rcp_no
        self.ele_id = ele_id
        self.dcm_no = dcm_no
        self._offset = offset
        self._length = length
        self._dtd = dtd
        self._html = None
        if not lazy_loading:
            self.load()

    @property
    def html(self):
        """ html 반환

        Returns
        -------
        str
            page html

        """
        if self._html is None:
            self.load()
        return self._html

    def load(self):
        """ page loading 함수 """
        def change_url(bs, tag):
            tags = bs.find_all(attrs={tag: re.compile(r'.*')})
            if tags:
                for t in tags:
                    t[tag] = "http://dart.fss.or.kr" + t[tag]
            return bs

        def add_prefix(match_obj):
            return r"window.open('http://dart.fss.or.kr" + match_obj.group(1) + r"'"

        payload = {
            'rcpNo': self.rcp_no,
            'dcmNo': self.dcm_no,
            'eleId': self.ele_id,
            'offset': self._offset,
            'length': self._length,
            'dtd': self._dtd
        }
        html = request.get(url=self._BASE_URL_, payload=payload, referer=self._BASE_URL_).content
        try:
            html = html.decode()
        except UnicodeDecodeError:
            html = html.decode('cp949')
        finally:
            soup = BeautifulSoup(html, 'html.parser')
            meta = soup.find('meta', {'content': re.compile(r'charset')})
            if meta:
                meta['content'] = meta['content'].replace('euc-kr', 'utf-8')

            soup = change_url(soup, 'href')
            soup = change_url(soup, 'src')

            html = str(soup)
            html = re.sub(r'window.open\(\'(.*?)\'', add_prefix, html)

            self._html = html

    def to_dict(self, summary=True) -> Dict[str, str]:
        """ dict 타입으로 반환

        Returns
        -------
        dict
            title, rcp_no, ele_id를 dict 타입으로 반환

        """
        info = dict()
        info['title'] = self.title
        info['ele_id'] = self.ele_id
        if not summary:
            info['rcp_no'] = self.rcp_no
            info['dcm_no'] = self.dcm_no
            info['offset'] = self._offset
            info['length'] = self._length
            info['dtd'] = self._dtd
        return info

    def __repr__(self) -> str:
        from pprint import pformat
        return pformat(self.to_dict(summary=False))

    def _repr_html_(self) -> str:
        if self.html is None:
            self.load()
        if len(self.html) == 0:
            html = 'blank page'
        else:
            html = self.html
        base64_html = base64.b64encode(bytes(html, 'utf-8')).decode('utf-8')
        return r'<iframe src="data:text/html;base64,' + base64_html + r'" style="width:100%; height:500px;"></iframe>'

    def __str__(self) -> str:
        from pprint import pformat
        return pformat(self.to_dict())


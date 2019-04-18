# -*- coding: utf-8 -*-

import re
import os
import base64

from typing import Dict
from bs4 import BeautifulSoup
from ._utils import request_get


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
    html: str
        페이지의 HTML 값

    """

    _BASE_URL_ = 'http://dart.fss.or.kr/report/viewer.do'

    def __init__(self, title: str, rcp_no: str, dcm_no: str, ele_id: str, offset: str, length: str, dtd: str):

        def change_url(bs, tag):
            tags = bs.find_all(attrs={tag: re.compile(r'.*')})
            if tags:
                for t in tags:
                    t[tag] = "http://dart.fss.or.kr" + t[tag]
            return bs

        def add_prefix(match_obj):
            return r"window.open('http://dart.fss.or.kr" + match_obj.group(1) + r"'"

        self.title = title
        self.rcp_no = rcp_no
        self.ele_id = ele_id
        self.dcm_no = dcm_no
        self._offset = offset
        self._length = length
        self._dtd = dtd

        params = {
            'rcpNo': rcp_no,
            'dcmNo': dcm_no,
            'eleId': ele_id,
            'offset': offset,
            'length': length,
            'dtd': dtd
        }
        html = request_get(url=self._BASE_URL_, params=params).content
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

            self.html = html

    def to_dict(self) -> Dict[str, str]:
        """ dict 타입으로 반환

        Returns
        -------
        dict
            title, rcp_no, ele_id를 dict 타입으로 반환

        """

        return {'title': self.title,
                'rcp_no': self.rcp_no,
                'ele_id': self.ele_id}

    def to_file(self, path: str, filename: str = None) -> None:
        """ 파일로 저장

        Parameters
        ----------
        path: str
            저장되는 위치
        filename: str, optional
            파일 이름

        """
        if not os.path.exists(path):
            os.makedirs(path)
        if filename is None:
            file = '{}_{}_{}.html'.format(self.rcp_no, self.ele_id, self.title)
        else:
            file = str(filename) + '.html'
        path = os.path.join(path, file)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(self.html)

    def __repr__(self) -> str:
        from pprint import pformat
        return pformat(self.to_dict())

    def _repr_html_(self) -> str:
        if len(self.html) == 0:
            html = 'blank page'
        else:
            html = self.html
        base64_html = base64.b64encode(bytes(html, 'utf-8')).decode('utf-8')
        return r'<iframe src="data:text/html;base64,' + base64_html + r'" style="width:100%; height:500px;"></iframe>'

    def __str__(self) -> str:
        from pprint import pformat
        return pformat(self.to_dict())


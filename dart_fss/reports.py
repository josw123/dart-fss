# -*- coding: utf-8 -*-

import re
import multiprocessing as mp

from typing import Dict, List, Union

from bs4 import BeautifulSoup, Comment
from tqdm import tqdm

from .markets import get_market_name
from .types import RMK_TYPES
from .pages import Page
from ._utils import dict_to_html, request_get
from .xbrl import get_xbrl_from_website, DartXbrl


def loading_page(r):
    template = ['rcp_no', 'dcm_no', 'ele_id', 'offset', 'length', 'dtd']

    leaf = {
        'title': re.findall(r'text:\s\"(.*?)\"', r)[0].replace(' ', '')
    }

    view_doc = re.findall(r'viewDoc\((.*?)\)', r)
    data = [x.strip() for x in view_doc[0].replace("'", "").split(',')]
    data = [0 if x == 'null' else x for x in data]
    for idx, _ in enumerate(template):
        leaf[template[idx]] = data[idx]
    new_page = Page(**leaf)
    return new_page


class Report(object):
    """ DART 공시 리포트 정보를 담고 있는 클래스

    DART 공시 리포트 정보를 담고 있는 클래스.
    개별 페이지는 즉시 Loading 되지 않고, 페이지 요청시 Lazy loading 된다.

    Attributes
    ----------
    crp_cls: str
        법인구분 : Y(유가), K(코스닥), N(코넥스), E(기타)
    crp_nm: str
        회사(증권) 정보
    crp_cd: str
        종목 코드
    rpt_nm: str
        공시구분+보고서명+기타정보
    rcp_no: str
        접수번호
    flr_nm: str
        공시 제출인명
    rcp_dt: str
        공시 접수일자(YYYYMMDD)
    rmk: str
        조합된 문자로 RMK_TYPES 참고

    """
    _DART_URL_ = 'http://dart.fss.or.kr'
    _REPORT_URL_ = _DART_URL_ + '/dsaf001/main.do'
    _DOWNLOAD_URL_ = _DART_URL_ + '/pdf/download/main.do'

    def __init__(self, crp_cls: str, crp_nm: str, crp_cd: str, rpt_nm: str,
                 rcp_no: str, flr_nm: str, rcp_dt: str, rmk: str):
        self.crp_cls = crp_cls
        self.crp_nm = crp_nm
        self.crp_cd = crp_cd
        self.rpt_nm = rpt_nm
        self.rcp_no = rcp_no
        self.flr_nm = flr_nm
        self.rcp_dt = rcp_dt
        self.rmk = rmk.strip()
        self._pages = None
        self._xbrl_url = None
        self._xbrl = None

    def to_dict(self) -> Dict[str, str]:
        """ dict 타입으로 정보 반환

        Returns
        -------
        dict
            리포트 정보

        """

        pages = 'Not loaded' if self._pages is None \
            else [x.to_dict() for x in self._pages]

        info = {
            'crp_cls': self.crp_cls,
            'crp_nm': self.crp_nm,
            'crp_cd': self.crp_cd,
            'rpt_nm': self.rpt_nm,
            'rcp_no': self.rcp_no,
            'flr_nm': self.flr_nm,
            'rcp_dt': self.rcp_dt,
            'rmk': self.rmk
        }

        if self._xbrl_url is not None:
            info['xbrl_url'] = self._xbrl_url
        info['pages'] = pages

        return info

    def to_file(self, path: str = None) -> None:
        """ 리포트 파일로 저장

        리포트 페이지를 각각 html 파일 형태로 저장. 각각의 페이지가 따로 저장됨

        Parameters
        ----------
        path: str
            파일 저장 경로

        """
        import os

        if self._pages is None:
            self.load_page()

        path = r'./{}/{}'.format(self.crp_nm, self.rpt_nm) if path is None else path
        path = os.path.abspath(path)
        if not os.path.exists(path):
            os.makedirs(path)

        # 파일명에 허용되지 않는 특수문자
        sub_sc = re.compile(r'\/|\\|\?|\%|\*|\||\"|\<|\>')
        for idx, page in enumerate(tqdm(self._pages, desc='Save files', unit='page')):
            page_title = sub_sc.sub('_', page.title)
            page.to_file(path, '{}_{}'.format(idx, page_title))

    @property
    def pages(self) -> List[Page]:
        """list of Page: Page 리스트"""
        if self._pages is None:
            self.load_page()

        return self._pages

    @property
    def xbrl(self) -> Union[DartXbrl, list]:
        """DartXbrl or list of DartXbrl: DartXbrl 반환"""
        if self._xbrl is None:
            self.load_xbrl()
        return self._xbrl

    def load_page(self, **kwargs) -> List[Page]:
        """ 페이지들의 HTML을 불러오는 함수

        Parameters
        ----------
        **kwargs
            includes에 포함된 단어가 Page 타이틀에 포함된 경우만 로딩됨
            excludes에 포함된 단어가 Page 타이틀에 포함되지 않은 경우만 페이지 로딩됨
            index는 특정 index만 로딩됨
        Returns
        -------
        list of Page
            로딩된 페이지 리스트 반환

        """
        def get_pattern(data, pattern, filter_type):
            if isinstance(pattern, str):
                patterns = '{}'.format(pattern)
            elif isinstance(pattern, list):
                patterns = r'(' + '|'.join(pattern) + ')'
            else:
                raise ValueError('Invalid includes')

            if filter_type == 'includes':
                def condition(x): return re.search(patterns, x)
            elif filter_type == 'excludes':
                def condition(x): return not re.search(patterns, x)
            else:
                raise ValueError('Invalid types')
            data = [r for r in data if condition(r)]
            return data

        params = dict(rcpNo=self.rcp_no)
        resp = request_get(url=self._REPORT_URL_, params=params)

        raw = re.findall(r'TreeNode\({(.*?)}\)', resp.text, re.S)

        includes = kwargs.get('includes')
        if includes is not None:
            raw = get_pattern(raw, includes, 'includes')

        excludes = kwargs.get('excludes')
        if excludes is not None:
            raw = get_pattern(raw, excludes, 'excludes')

        index = kwargs.get('index')
        if index is not None:
            raw = [r for idx, r in enumerate(raw) if idx in index]

        progressbar_disable = kwargs.get('progressbar_disable', False)

        process_cnt = mp.cpu_count() - 1
        if process_cnt > 0:
            pool = mp.Pool(processes=process_cnt)
            tree = list(tqdm(pool.imap(loading_page, raw), desc='Loading', leave=False,
                             total=len(raw), unit='page', disable=progressbar_disable))
            pool.close()
            pool.join()
        else:
            tree = [loading_page(r) for r in tqdm(raw, desc='Loading', leave=False,
                                                  total=len(raw), unit='page', disable=progressbar_disable)]
        tree = [x for x in tree if x]
        tree.sort(key=lambda x: int(x.ele_id))

        if len(tree) > 0:
            dcm_no = tree[0].dcm_no
            self._get_xbrl(dcm_no)

        if includes is None and excludes is None and index is None:
            self._pages = tree

        return tree

    def load_xbrl(self) -> None:
        """XBRL 파일 로드 함수"""
        if self._xbrl_url is None:
            self.load_page(index=[0], progressbar_disable=True)

        if self._xbrl_url is not None:
            xbrl = get_xbrl_from_website(self._xbrl_url)
            if len(xbrl) == 1:
                self._xbrl = xbrl[0]
            elif len(xbrl) > 1:
                self._xbrl = xbrl
            else:
                self._xbrl = None

    def _get_xbrl(self, dcm_no):
        params = dict(rcp_no=self.rcp_no, dcm_no=dcm_no)
        resp = request_get(url=self._DOWNLOAD_URL_, params=params)
        soup = BeautifulSoup(resp.text, 'html.parser')
        comment = soup.find_all(string=lambda text: isinstance(text, Comment))
        for c in comment:
            if len(re.findall(r'IFRS', c.string, re.IGNORECASE)) > 0:
                a_href = c.find_next('a')
                attrs = a_href.attrs.get('href')
                if re.search('none', attrs):
                    return
                xbrl_url = self._DART_URL_ + attrs
                self._xbrl_url = xbrl_url

    def __getitem__(self, item):
        if self._pages is None:
            self.load_page()

        return self._pages[item]

    def __len__(self):
        return len(self.pages)

    def __repr__(self):
        from pprint import pformat

        dict_data = self.to_dict()
        if self._pages is None:
            dict_data['pages'] = 'Not loaded'

        return pformat(dict_data)

    def _repr_html_(self):
        return dict_to_html(self.to_dict(), header=['Label', 'Data'])

    def __str__(self):
        from pprint import pformat

        if self._pages is None:
            page_list = 'Not loaded'
        else:
            page_list = [page.title for page in self._pages]

        summary = {
            '구분': get_market_name(self.crp_cls),
            '종목명': self.crp_nm,
            '종목코드': self.crp_cd,
            '공시구분': self.rpt_nm,
            '접수번호': self.rcp_no,
            '공시제출인': self.flr_nm,
            '접수일자': self.rcp_dt,
            '비고': RMK_TYPES[self.rmk] if len(self.rmk) > 0 else '',
            '목차': page_list
        }

        if self._xbrl_url is not None:
            summary['XBRL_URL'] = self._xbrl_url

        return pformat(summary)



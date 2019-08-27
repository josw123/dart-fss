# -*- coding: utf-8 -*-
import os
import re
import copy

from urllib.parse import unquote, parse_qs

from bs4 import BeautifulSoup

from dart_fss.pages import Page
from dart_fss._utils import dict_to_html, request_get, compare_str, create_folder, unzip, search_file
from dart_fss.xbrl import get_xbrl_from_file
from dart_fss.regex import str_to_regex


class Report(object):
    """ 보고서 클래스
    DART 재무제표 보고서 정보를 담고 있는 클래스

    Attributes
    ----------
    rcp_no: str
        보고서 번호
    dcm_no: str
        document 번호
    info: dict of {str: str}
        기타 보고서 정보
    html: BeautifulSoup
        보고서 HTML
    related_reports: list of RelatedReport
        연관 보고서 리스트
    attached_reports: list of AttachedReport
        첨부 보고서 리스트
    attached_files: list of AttachedFile
        첨부 파일 리스트
    xbrl: DartXbrl
        XBRL 파일이 있을시 DartXbrl 클래스
    """
    _DART_URL_ = 'http://dart.fss.or.kr'
    _REPORT_URL_ = _DART_URL_ + '/dsaf001/main.do'
    _DOWNLOAD_URL_ = _DART_URL_ + '/pdf/download/main.do'

    def __init__(self, **kwargs):
        """
        Parameters
        ----------
        rcp_no: str
            보고서 번호
        dcm_no: str
            document 번호
        info: dict of {str:str}
            기타 보고서 정보
        lazy_loading: bool
            True: lazy loading / False: 보고서 로드시 모든 정보 로딩
        """
        self.rcp_no = kwargs.get('rcp_no')
        if self.rcp_no is None:
            raise ValueError('rcp_no must be not None')
        self.dcm_no = kwargs.get('dcm_no')

        self.info = copy.deepcopy(kwargs)
        self.info.pop('rcp_no')
        if self.dcm_no:
            self.info.pop('dcm_no')
        
        self.html = None
        self._pages = None
        self._xbrl = None
        self._related_reports = None
        self._attached_files = None
        self._attached_reports = None

        lazy_loading = kwargs.get('lazy_loading', True)
        if not lazy_loading:
            self.load()

    def _get_report(self):
        """ 보고서 html 불러오기"""
        params = dict(rcpNo=self.rcp_no)
        if self.dcm_no:
            params['dcmNo'] = self.dcm_no
        resp = request_get(url=self._REPORT_URL_, params=params)
        self.html = BeautifulSoup(resp.text, 'html.parser')

    @property
    def related_reports(self):
        """ 연관 보고서 반환

        Returns
        -------
        list of RelatedReport
            연관 보고서리스트 반환

        """
        if self._related_reports is None:
            self.extract_related_reports()
        return self._related_reports

    def extract_related_reports(self):
        """ 연관 보고서 리스트 추출

        Returns
        -------
        list of RelatedReport
            연관 보고서리스트 반환

        """
        if self.html is None:
            self._get_report()
        results = []
        soup = self.html
        family = soup.find('select', id='family')
        related_reports = family.find_all('option')
        for report in related_reports:
            value = report.attrs.get('value')
            if compare_str(value, 'null'):
                continue
            rpt_nm = re.sub(r'\s+', ' ', report.text).strip()
            rcp_no = value.split('=')[1]
            if compare_str(self.rcp_no, rcp_no):
                if self.info.get('rpt_nm') is None:
                    self.info['rpt_nm'] = rpt_nm
                continue
            info = {'rcp_no': rcp_no, 'rpt_nm': rpt_nm, 'parent': self}
            results.append(RelatedReport(**info))
        self._related_reports = sorted(results, key=lambda x: x.rcp_no, reverse=True)
        return self._related_reports

    @property
    def pages(self):
        """ 보고서 page 반환

        Returns
        -------
        list of Page
            보고서의 page 리스트 반환

        """
        if self._pages is None:
            self.extract_pages()
        return self._pages

    def extract_pages(self):
        """ 보고서 page 리스트 추출

        Returns
        -------
        list of Page
            보고서의 page 리스트 반환
        """
        if self.html is None:
            self._get_report()
        results = []
        raw_data = re.findall(r'TreeNode\({(.*?)}\)', self.html.text, re.S)
        for raw in raw_data:
            template = ['rcp_no', 'dcm_no', 'ele_id', 'offset', 'length', 'dtd']

            leaf = {
                'title': re.findall(r'text:\s\"(.*?)\"', raw)[0].replace(' ', '')
            }

            view_doc = re.findall(r'viewDoc\((.*?)\)', raw)
            data = [x.strip() for x in view_doc[0].replace("'", "").split(',')]
            data = [0 if x == 'null' else x for x in data]
            for idx, _ in enumerate(template):
                leaf[template[idx]] = data[idx]
            results.append(Page(**leaf))
        self._pages = results
        return self._pages

    @property
    def attached_files(self):
        """ 첨부된 파일 리스트 반환

        Returns
        -------
        list of AttachedFile
            첨부된 파일 리스트

        """
        if self._attached_files is None:
            self.extract_attached_files()
        return self._attached_files

    def extract_attached_files(self):
        """ 첨부된 파일 리스트 추출 및 반환

        Returns
        -------
        list of AttachedFile
            첨부된 파일리스트

        """
        if self.html is None:
            self._get_report()
        results = []
        a_href = self.html.find('a', href='#download')
        a_onclick = a_href.attrs.get('onclick', '')
        raw_data = re.search(r'openPdfDownload\(.*?(\d+).*?(\d+).*?\)', a_onclick)
        if raw_data is None:
            return results

        rcp_no = raw_data.group(1)
        dcm_no = raw_data.group(2)

        params = dict(rcp_no=rcp_no, dcm_no=dcm_no)
        resp = request_get(url=self._DOWNLOAD_URL_, params=params)

        soup = BeautifulSoup(resp.text, 'html.parser')
        tr_list = soup.find_all('tr')
        attached_files = []

        for tr in tr_list:
            if tr.find('a'):
                td_list = tr.find_all('td')
                filename = td_list[0].text.strip()
                file_url = td_list[1].a.get('href')
                if not file_url:
                    continue
                info = dict()
                info['rcp_no'] = self.rcp_no
                info['url'] = file_url
                info['filename'] = filename
                attached_files.append(AttachedFile(**info))
        self._attached_files = attached_files
        return self._attached_files

    @property
    def attached_reports(self):
        """ 첨부된 보고서 반환

        Returns
        -------
        list of AttachedReport
            첨부된 보고서 리스트

        """
        if self._attached_reports is None:
            self.extract_attached_reports()
        return self._attached_reports

    def extract_attached_reports(self):
        """ 첨부된 보고서 리스트 추출 및 반환

        Returns
        -------
        list of AttachedReport
            첨부된 보고서 리스트

        """
        if self.html is None:
            self._get_report()
        soup = self.html
        attached = soup.find('p', class_='f_none')
        attached_list = attached.find_all('option')
        attached_reports = []

        for docs in attached_list:
            rpt_nm = re.sub(r'\s+', ' ', docs.text).strip()
            docs_url = docs.attrs.get('value')
            if compare_str(docs_url, 'null'):
                pass
            else:
                info = dict()
                parsed = parse_qs(docs_url)
                info['rcp_no'] = parsed.get('rcpNo')[0]
                info['dcm_no'] = parsed.get('dcmNo')[0]
                info['rpt_nm'] = rpt_nm
                info['parent'] = self
                attached_reports.append(AttachedReport(**info))
        self._attached_reports = sorted(attached_reports, key=lambda x: x.rcp_no, reverse=True)
        return self._attached_reports

    def load(self):
        """ 페이지들의 HTML을 불러오는 함수 """
        self._get_report()
        self.extract_related_reports()
        self.extract_attached_reports()
        self.extract_pages()
        self.extract_attached_files()
        self.find_all()

    def find_all(self, **kwargs):
        """ 보고서의 Page 재묵을 검색하여 검색된 Page 리스틑 반환하는 함수

         Other Parameters
        ----------------
        includes: str
            Page 제목에 포함될 단어
        excludes: str
            Page 제목에 포함되지 않을 단어
        scope: list
            검색할 검색 범위(default: pages, related_reports, attached_reports, attached_files)
        options: dict of {str: bool}

        Returns
        -------
        list or dict of {str: list}
            검색된 Page 리스트
        """
        includes = kwargs.get('includes')
        excludes = kwargs.get('excludes')
        scope = kwargs.get('scope', ['pages', 'related_reports', 'attached_reports', 'attached_files'])
        options = kwargs.get('options')

        def determinant(value):
            det1 = str_to_regex(includes).search(value) if includes else True
            det2 = not str_to_regex(excludes).search(value) if excludes else True
            return det1 and det2

        def pages(): return [x for x in self.pages if determinant(x.title)]

        def related_reports():
            if options and options.get('title'):
                res = [y for x in self.related_reports for y in x.find_all(**kwargs) if determinant(x.title)]
            else:
                res = [y for x in self.related_reports for y in x.find_all(**kwargs)]
            return res

        def attached_reports():
            if options and options.get('title'):
                res = [y for x in self.attached_reports for y in x.find_all(**kwargs) if determinant(x.info['rpt_nm'])]
            else:
                res = [y for x in self.attached_reports for y in x.find_all(**kwargs)]
            return res

        def attached_files(): return [x for x in self.attached_files if determinant(x.filename)]

        func_set = {
            'pages': pages,
            'related_reports': related_reports,
            'attached_reports': attached_reports,
            'attached_files': attached_files
        }

        dataset = dict()
        for s in scope:
            dataset[s] = func_set[s]()
        return dataset if len(dataset) > 1 else dataset[scope[0]]

    @property
    def xbrl(self):
        """ XBRL 데이터 반환"""
        import tempfile
        if self._xbrl is None:
            xbrl = self._get_xbrl()
            if xbrl:
                xbrl_list = []
                with tempfile.TemporaryDirectory() as path:
                    file_path = xbrl.download(path)
                    extract_path = unzip(file_path)
                    xbrl_file = search_file(extract_path)
                    for file in xbrl_file:
                        xbrl = get_xbrl_from_file(file)
                        xbrl_list.append(xbrl)
                self._xbrl = xbrl_list[0]
        return self._xbrl

    def _get_xbrl(self):
        """ XBRL 첨부파일 검색"""
        query = {
            'includes': 'IFRS OR XBRL',
            'scope': ['attached_files']
        }
        attached_files = self.find_all(**query)
        return attached_files[0] if len(attached_files) > 0 else None

    def to_dict(self, summary=True):
        """ Report 정보를 Dictionary 형태로 반환

        Parameters
        ----------
        summary: bool, optional
            True 요약정보 / False 모든 정보
        Returns
        -------
        dict of {str: str or list}
            Report 정보
        """
        info = dict()
        info['rcp_no'] = self.rcp_no
        info.update(self.info)
        if not summary:
            xbrl = self._get_xbrl()
            if xbrl:
                info['xbrl'] = xbrl.filename
            related_reports = [x.to_dict() for x in self.related_reports]
            if len(related_reports) > 0:
                info['related_reports'] = related_reports
            attached_reports = [x.to_dict() for x in self.attached_reports]
            if len(attached_reports) > 0:
                info['attached_reports'] = attached_reports
            attached_files = [x.to_dict() for x in self.attached_files]
            if len(attached_files) > 0:
                info['attached_files'] = attached_files
            info['pages'] = [x.to_dict() for x in self.pages]
        return info

    def __getattr__(self, item):
        if item in self.info:
            return self.info[item]
        else:
            error = "'{}' object has no attribute '{}'".format(type(self).__name__, item)
            raise AttributeError(error)

    def __getitem__(self, item):
        return self.pages[item]

    def __len__(self):
        return len(self.pages)

    def __repr__(self):
        from pprint import pformat
        dict_data = self.to_dict()
        return pformat(dict_data)

    def _repr_html_(self):
        return dict_to_html(self.to_dict(summary=False), header=['Label', 'Data'])


class RelatedReport(Report):
    """ 연관된 보고서 클래스
block_size = 8192
    연관 보고서 정보를 담고 있는 클래스
    Report 클래스 상속

    Attributes
    ----------
    parent: Report
        상위 보고서

    """
    def __init__(self, **kwargs):
        self.parent = kwargs.get('parent')
        if self.parent is None:
            raise ValueError('RelatedReport must have parent')
        kwargs.pop('parent')
        super().__init__(**kwargs)

    @property
    def related_reports(self):
        """ related_reports overriding """
        return []
    
    def extract_related_reports(self):
        """ extract_related_reports overriding"""
        return []

    def to_dict(self, summary=True):
        """ Report 정보를 Dictionary 형태로 반환

        Parameters
        ----------
        summary: bool, optional
            True 요약정보 / False 모든 정보
        Returns
        -------
        dict of {str: str or list}
            Report 정보
        """
        info = dict()
        if not summary:
            info['parent'] = self.parent.rcp_no
            info['rcp_no'] = self.rcp_no
        info.update(self.info)
        if not summary:
            attached_reports = [x.to_dict() for x in self.attached_reports]
            if len(attached_reports) > 0:
                info['attached_reports'] = attached_reports
            attached_files = [x.to_dict() for x in self.attached_files]
            if len(attached_files) > 0:
                info['attached_files'] = attached_files
            info['pages'] = [x.to_dict() for x in self.pages]
        return info
    
    def find_all(self, **kwargs):
        """
        보고서의 Page 재묵을 검색하여 검색된 Page 리스틑 반환하는 함수

         Other Parameters
        ----------------
        includes: str
            Page 제목에 포함될 단어
        excludes: str
            Page 제목에 포함되지 않을 단어

        Returns
        -------
        list or dict of {str: list}
            검색된 Page 리스트

        """
        includes = kwargs.get('includes')
        excludes = kwargs.get('excludes')

        def determinant(value):
            det1 = str_to_regex(includes).search(value) if includes else True
            det2 = not str_to_regex(excludes).search(value) if excludes else True
            return det1 and det2
        
        return [
            x for x in self.pages if determinant(x.title)
        ]


class AttachedReport(RelatedReport):
    """
    첨부된 보고서 클래스

    첨부된 보고서 정보를 담고 있는 클래스

    """
    @property
    def attached_reports(self):
        return []

    def extract_attached_reports(self):
        return []

    def to_dict(self, summary=True):
        """ Report 정보를 Dictionary 형태로 반환

        Parameters
        ----------
        summary: bool, optional
            True 요약정보 / False 모든 정보
        Returns
        -------
        dict of {str: str or list}
            Report 정보
        """
        info = dict()
        if not summary:
            info['parent'] = self.parent.rcp_no
            info['rcp_no'] = self.rcp_no
        info.update(self.info)
        if not summary:
            info['pages'] = [x.to_dict() for x in self.pages]
        return info


class AttachedFile(object):
    """
    첨부파일 클래스


    보고서에 첨부된 파일의 정보를 담고 있는 클래스


    Attributes
    ----------
    rcp_no : str
        첨부파일 페이지 번호
    url : str
        첨부파일 url
    filename : str
        첨부파일명

    """
    _DART_URL_ = 'http://dart.fss.or.kr'

    def __init__(self, rcp_no, url, filename):
        self.rcp_no = rcp_no
        self.url = self._DART_URL_ + url
        self.filename = filename

    def to_dict(self, summary=True):
        info = dict()
        info['filename'] = self.filename
        if not summary:
            info['related_report'] = self.rcp_no
            info['url'] = self.url
        return info

    def __repr__(self):
        from pprint import pformat
        return pformat(self.to_dict())

    def _repr_html_(self):
        return dict_to_html(self.to_dict(summary=False), header=['Label', 'Data'])

    def download(self, path):
        """
        첨부파일 다운로드 Method

        Parameters
        ----------
        path: str
            다운롣드 받을 경로

        Returns
        -------
        str
            다운받은 첨부파일 경로

        """
        from dart_fss.spinner import Spinner

        create_folder(path)

        url = self.url
        r = request_get(url=url, stream=True)
        headers = r.headers.get('Content-Disposition')
        if not re.search('attachment', headers):
            raise Exception('invalid data found')

        # total_size = int(r.headers.get('content-length', 0))
        block_size = 8192

        filename = unquote(re.findall(r'filename="(.*?)"', headers)[0])

        filename = '{}_{}'.format(self.rcp_no, filename)
        spinner = Spinner('Downloading ' + filename)
        spinner.start()

        file_path = os.path.join(path, filename)
        with open(file_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=block_size):
                if chunk is not None:
                    f.write(chunk)
        r.close()
        spinner.stop()
        return file_path

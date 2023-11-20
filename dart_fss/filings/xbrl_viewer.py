import re
import base64
from typing import Dict

from bs4 import BeautifulSoup
from urllib.parse import urljoin

from dart_fss.utils import dict_to_html, request, unzip, search_file
from dart_fss.xbrl import get_xbrl_from_file
from dart_fss.utils.regex import str_to_regex
from dart_fss.api.finance import download_xbrl

class XBRLViewer(object):
    """ DART에서 제공하는 XBRL Viewer 클래서
    DART에서 제공하는 XBRL Viewer를 이용하여 XBRL 정보를 가져오는 클래스

    Attributes
    ----------
    rcp_no:str
        보고서 번호
    """
    _DART_URL_ = 'https://dart.fss.or.kr'
    _OPENDART_URL_ = 'https://opendart.fss.or.kr/'
    _VIEWER_URL_ = _OPENDART_URL_ + '/xbrl/viewer/main.do'
    _DOWNLOAD_URL_ = _OPENDART_URL_ + '/xbrl/viewer/download.do'

    def __init__(self, rcp_no: str, lazy_loading=True):
        self.rcp_no = rcp_no
        self.html = None
        self._xbrl = None
        self._pages = None
        self._attached_files = None
        if not lazy_loading:
            self.load()

    def _get_report(self):
        """ 보고서 html 불러오기"""
        payload = dict(rcpNo=self.rcp_no)
        resp = request.get(url=self._VIEWER_URL_, payload=payload, referer=self._DART_URL_)
        self.html = BeautifulSoup(resp.text, 'html.parser')

    def extract_pages(self):
        """ 보고서 page 리스트 추출

        Returns
        -------
        list of Page
            보고서의 page 리스트 반환
        """
        if self.html is None:
            self._get_report()

        tds = self.html.find_all('td', {'class': 'scd'})
        self._pages = []
        for td in tds:
            title = td.get_text().strip()
            # Javascript was changed in newdart
            regex_page = re.compile(r'onclick=\"viewDoc\((.*)\)\"')
            pageinfo = regex_page.findall(str(td))
            pageinfo = [x.replace("'", "").split(',') for x in pageinfo][0]
            self._pages.append(XBRLViewerPage(title, pageinfo[0].strip(), pageinfo[1].strip(), pageinfo[2].strip()))
        return self._pages

    def extract_attached_files(self):
        """ 보고서 첨부파일 리스트 추출

        Returns
        -------
        list of XBRLViewerAttachedFile
            보고서의 첨부파일 리스트 반환
        """
        if self.html is None:
            self._get_report()

        self._attached_files = []
        regex_page = re.compile(r'onclick=\"openDownload\((.*)\)')
        attached_files = regex_page.findall(str(self.html))
        attached_files = [x.replace("'", "").split(',') for x in attached_files]
        if len(attached_files) > 0:
            url = self._DOWNLOAD_URL_
            payload = {
                'rcpNo': attached_files[0][0].strip(),
                'dcmNo': attached_files[0][1].strip(),
                'lang': attached_files[0][2].strip()
            }
            html = request.get(url=url, payload=payload, referer=self._VIEWER_URL_).content
            try:
                html = html.decode()
            except UnicodeDecodeError:
                html = html.decode('cp949')
            finally:
                soup = BeautifulSoup(html, 'html.parser')
                trs = soup.find_all('tr')
                for tr in trs[1:]:
                    tds = tr.find_all('td')
                    if len(tds) == 2:
                        filename = tds[0].text
                        url_path = tds[1].find('a')['href']
                        self._attached_files.append(XBRLViewerAttachedFile(self.rcp_no, url_path, filename, self._VIEWER_URL_))

        return self._attached_files

    def load(self):
        """ xbrl viewer loading 함수 """
        self._get_report()
        self.extract_pages()
        self.extract_attached_files()

    @property
    def rcept_no(self):
        return self.rcp_no

    @rcept_no.setter
    def rcept_no(self, rcept_no):
        self.rcp_no = rcept_no

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

    def find_all(self, **kwargs):
        """ 보고서의 Page 재묵을 검색하여 검색된 Page 리스틑 반환하는 함수

         Other Parameters
        ----------------
        includes: str
            Page 제목에 포함될 단어
        excludes: str
            Page 제목에 포함되지 않을 단어
        scope: list
            검색할 검색 범위(default: pages, attached_files)
        options: dict of {str: bool}

        Returns
        -------
        list or dict of {str: list}
            검색된 Page 리스트
        """
        includes = kwargs.get('includes')
        excludes = kwargs.get('excludes')
        scope = kwargs.get('scope', ['pages', 'attached_files'])
        options = kwargs.get('options')

        def determinant(value):
            det1 = str_to_regex(includes).search(value) if includes else True
            det2 = not str_to_regex(excludes).search(value) if excludes else True
            return det1 and det2

        def pages(): return [x for x in self.pages if determinant(x.title)]

        def attached_files(): return [x for x in self.attached_files if determinant(x.filename)]

        func_set = {
            'pages': pages,
            'attached_files': attached_files
        }

        dataset = dict()
        for s in scope:
            dataset[s] = func_set[s]()
        return dataset if len(dataset) > 1 else dataset[scope[0]]

    @property
    def xbrl(self):
        if self._xbrl is None:
            self.load_xbrl()
        return self._xbrl

    def load_xbrl(self):
        """ XBRL 데이터 반환"""
        import tempfile
        if self._xbrl is None:
            with tempfile.TemporaryDirectory() as path:
                try:
                    file_path = download_xbrl(path=path, rcept_no=self.rcept_no)
                    self._xbrl = get_xbrl_from_file(file_path)
                except FileNotFoundError:
                    xbrl_attached = self._get_xbrl()
                    if xbrl_attached is not None:
                        zip_path = xbrl_attached.download(path=path)
                        folder_path = unzip(zip_path['full_path'])
                        file = search_file(folder_path)
                        if len(file) > 0:
                            self._xbrl = get_xbrl_from_file(file[0])
                    else:
                        self._xbrl = None
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
        if not summary:
            xbrl = self._get_xbrl()
            if xbrl:
                info['xbrl'] = xbrl.filename
            attached_files = [x.to_dict() for x in self.attached_files]
            if len(attached_files) > 0:
                info['attached_files'] = attached_files
            info['pages'] = [x.to_dict() for x in self.pages]
        return info

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


class XBRLViewerPage(object):
    """ DART XBRL Viewer의 페이지 클래스

    DART XBRL Viewer의 개별 페이지 정보를 담고 있는 클래스.

    Attributes
    ----------
    xbrlExtSeq: str
        페이지의 xbrlExtSeq
    roleId: str
        페이지의 roleId
    lang: str
        페이지의 lang
    """

    _BASE_URL_ = 'https://opendart.fss.or.kr/xbrl/viewer/view.do'

    def __init__(self, title:str, xbrl_ext_seq: str, role_id: str, lang:str, lazy_loading=True):
        self.title = title
        self.xbrl_ext_seq = xbrl_ext_seq
        self.role_id = role_id
        self.lang = lang
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
        payload = {
            'xbrlExtSeq': self.xbrl_ext_seq,
            'roleId': self.role_id,
            'lang': self.lang
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
            else:
                head = soup.new_tag('head')
                metatag = soup.new_tag('meta')
                metatag.attrs['http-equiv'] = 'Content-Type'
                metatag.attrs['content'] = 'text/html'
                metatag.attrs['charset'] = 'utf-8'

                link = soup.new_tag('link')
                link.attrs['type'] = 'text/css'
                link.attrs['id'] = 'viewerCss'
                link.attrs['rel'] = 'stylesheet'
                link.attrs['href'] = 'https://opendart.fss.or.kr/xbrl/css/viewer.css'

                head.append(link)
                head.append(metatag)
                soup.insert(0, head)

            html = str(soup)
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
        info['xbrl_ext_seq'] = self.xbrl_ext_seq
        info['role_id'] = self.role_id
        info['lang'] = self.lang
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



class XBRLViewerAttachedFile(object):
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
    _OPENDART_URL_ = 'https://opendart.fss.or.kr'
    _REFPATH_ = _OPENDART_URL_ + '/xbrl/viewer/download.do'

    def __init__(self, rcp_no, path, filename, referer):
        self.rcp_no = rcp_no
        self.url = urljoin(self._REFPATH_, path)
        self.filename = filename.strip()
        self.referer = referer

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
        file_path = request.download(url=self.url, path=path, filename=self.filename, referer=self.referer)
        return file_path

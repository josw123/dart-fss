# -*- coding: utf-8 -*-
from dart_fss.auth import get_api_key
from dart_fss.utils import request, unzip, search_file


def download_xbrl(path: str, rcept_no: str, reprt_code: str = None) -> str:
    """ XBRL 파일 다운로드

    Parameters
    ----------
    path: str
        Download Path
    rcept_no: str
        접수번호
    reprt_code: str, optinal
        1분기보고서 : 11013 반기보고서 : 11012 3분기보고서 : 11014 사업보고서 : 11011

    Returns
    -------
    str
        xbrl file path

    """
    import tempfile

    with tempfile.TemporaryDirectory() as temp:
        url = 'https://opendart.fss.or.kr/api/fnlttXbrl.xml'

        # Set API KEY
        api_key = get_api_key()
        payload = {
            'crtfc_key': api_key,
            'rcept_no': rcept_no,
            'reprt_code': reprt_code
        }

        # Request Download
        resp = request.download(url=url, path=temp, payload=payload)
        download_path = resp['full_path']

        # Unzip File in User Cache Folder
        unzip_path = unzip(file=download_path, path=path)

        # Search XBRL file
        files = search_file(path=unzip_path)
        if len(files) == 0:
            raise FileNotFoundError('XBRL File Not Found')

        file = files[0]
        return file

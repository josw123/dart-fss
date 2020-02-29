# -*- coding: utf-8 -*-
from collections import OrderedDict

from dart_fss.auth import get_api_key
from dart_fss.utils import request, unzip, get_cache_folder, search_file, xml_to_dict


def get_corp_code() -> OrderedDict:
    """ DART에 등록되어있는 공시대상회사의 고유번호,회사명,대표자명,종목코드, 최근변경일자 다운로드

    Returns
    -------
    OrderedDict
        고유번호 및 회사 정보
    """
    import tempfile

    with tempfile.TemporaryDirectory() as path:
        url = 'https://opendart.fss.or.kr/api/corpCode.xml'

        # Set API KEY
        api_key = get_api_key()
        payload = {'crtfc_key': api_key}

        # Request Download
        resp = request.download(url=url, path=path, payload=payload)
        download_path = resp['full_path']
        cache_folder = get_cache_folder()

        # Unzip File in User Cache Folder
        unzip_path = unzip(file=download_path, path=cache_folder)

        # Search CORPCODE.xml
        files = search_file(path=unzip_path, filename='CORPCODE', extensions='xml')
        if len(files) == 0:
            raise FileNotFoundError('CORPCODE.xml Not Found')

        file = files[0]
        data = xml_to_dict(file)
        return data['result']['list']
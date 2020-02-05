# -*- coding: utf-8 -*-
from collections import OrderedDict

from dart_fss.auth import get_api_key
from dart_fss.utils import request, unzip, get_cache_folder, search_file, xml_to_dict


def get_crp_code() -> OrderedDict:
    """ Download CORPCODE.xml and convert xml file to OrderedDict

    Returns
    -------
    OrderedDict
        corp_code list in Open DART
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
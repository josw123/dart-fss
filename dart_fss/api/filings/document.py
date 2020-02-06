# -*- coding: utf-8 -*-
from dart_fss.auth import get_api_key
from dart_fss.utils import request


def download_document(path: str) -> str:
    """ 공시서류원본파일 다운로드

    Parameters
    ----------
    path: str
        download path

    Returns
    -------
    str
        download full path
    """
    url = 'https://opendart.fss.or.kr/api/document.xml'

    # Set API KEY
    api_key = get_api_key()
    payload = {'crtfc_key': api_key}

    resp = request.download(url=url, path=path, payload=payload)
    return resp['full_path']
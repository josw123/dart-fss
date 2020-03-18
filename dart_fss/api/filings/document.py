# -*- coding: utf-8 -*-
from dart_fss.auth import get_api_key
from dart_fss.utils import request


def download_document(path: str, rcept_no: str) -> str:
    """ 공시서류원본파일 다운로드

    Parameters
    ----------
    path: str
        download path
    rcept_no: str
        접수번호

    Returns
    -------
    str
        download full path
    """
    url = 'https://opendart.fss.or.kr/api/document.xml'

    # Set API KEY
    api_key = get_api_key()
    payload = {
        'crtfc_key': api_key,
        'rcept_no': rcept_no,
    }

    resp = request.download(url=url, path=path, payload=payload)
    return resp['full_path']
# -*- coding: utf-8 -*-
from dart_fss.auth import get_api_key
from dart_fss.utils import request, unzip

def get_crp_code():
    URL = 'https://opendart.fss.or.kr/api/corpCode.xml'
    api_key = get_api_key()
    payload = {
        'crtfc_key': api_key
    }
    response = request.get(url=URL, payload=payload, stream=True)
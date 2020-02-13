# -*- coding: utf-8 -*-
import re

from urllib.parse import urljoin
from dart_fss.auth import get_api_key
from dart_fss.utils import request
from dart_fss.errors import check_status

# corp_code check regular expression
corp_code_checker = re.compile(r'^[0-9]{8}$')
# bsns_year check regular expression
bsns_year_checker = re.compile(r'^[0-9]{4}$')
# reprt_code check regular expression
reptr_code_checker = re.compile(r'^1101[1-4]$')


def api_request(path: str, corp_code: str, bsns_year: str = None, reprt_code: str = None) -> dict:
    """ API Request Helper

    Parameters
    ----------
    path: str
        API Path
    corp_code: str
        Corporation Code (8 digits)
    bsns_year: str, optional
        Year (4 digits)
    reprt_code: str, optional
        Report code( Q1: 11013, half: 11012, Q3: 11014, Annual: 11011)

    Returns
    -------
    dict
        API Request Result
    """

    if corp_code and corp_code_checker.search(corp_code) is None:
        raise ValueError('corp_code must be 8 digits')

    if bsns_year and bsns_year_checker.search(bsns_year) is None:
        raise ValueError('bsns_year must be 4 digits')

    if reprt_code and reptr_code_checker.search(reprt_code) is None:
        raise ValueError('invalid reprt_code')

    # Open DART Base URL
    base = 'https://opendart.fss.or.kr/'
    # Request URL
    url = urljoin(base, path)

    # Get DART_API_KEY
    api_key = get_api_key()

    # Set payload
    payload = {
        'crtfc_key': api_key,
        'corp_code': corp_code,
        'bsns_year': bsns_year,
        'reprt_code': reprt_code,
    }

    # Request Data
    resp = request.get(url=url, payload=payload)

    # Convert Response to json
    dataset = resp.json()

    # Status Code Check
    check_status(**dataset)
    return dataset


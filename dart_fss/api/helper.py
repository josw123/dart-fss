# -*- coding: utf-8 -*-
import re

from urllib.parse import urljoin
from dart_fss.auth import get_api_key
from dart_fss.utils import request
from dart_fss.errors import check_status

# corp_code check regular expression
corp_code_checker = re.compile(r'^([0-9]{8})(,[0-9]{8})*$')
# bsns_year check regular expression
bsns_year_checker = re.compile(r'^[0-9]{4}$')
# reprt_code check regular expression
reptr_code_checker = re.compile(r'^1101[1-4]$')
# date check regular expression
date_checker = re.compile(r'^[0-9]{8}$')
# fs_div check regular expression
fs_div_checker = re.compile(r'CFS|OFS', re.IGNORECASE)
# sj_div check list
sj_div_checker = ('BS1', 'BS2', 'BS3', 'BS4', 'IS1', 'IS2', 'IS3', 'IS4', 'CIS1', 'CIS2', 'CIS3', 'CIS4', 'DCIS1',
                  'DCIS2', 'DCIS3', 'DCIS4', 'DCIS5', 'DCIS6', 'DCIS7', 'DCIS8', 'CF1', 'CF2', 'CF3', 'CF4', 'SCE1',
                  'SCE2')


def api_request(
        path: str,
        corp_code: str = None,
        bsns_year: str = None,
        reprt_code: str = None,
        bgn_de: str = None,
        end_de: str = None,
        fs_div: str = None,
        sj_div: str = None,
        api_key: str = None
) -> dict:
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
    bgn_de: str, optional
        Searching Start date (YYYYMMDD)
    end_de: str, optional
        Searching End date (YYYYMMDD)
    fs_div: str, optional
        CFS:Consolidated Financial Statements, OFS:Separate financial statements
    sj_div: str, optional
        Classification of financial statements(https://opendart.fss.or.kr/guide/detail.do?apiGrpCd=DS003&apiId=2020001)
    api_key: str, optional
        DART_API_KEY(If not set, use environment variable DART_API_KEY)
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

    if bgn_de and date_checker.search(bgn_de) is None:
        raise ValueError('invalid bgn_de')

    if end_de and date_checker.search(end_de) is None:
        raise ValueError('invalid end_de')

    if fs_div:
        if fs_div_checker.search(fs_div) is None:
            raise ValueError('fs_div must be CFS or OFS')
        fs_div = fs_div.upper()

    if sj_div:
        if sj_div not in sj_div_checker:
            raise ValueError('invalid sj_div')

    # Open DART Base URL
    base = 'https://opendart.fss.or.kr/'
    # Request URL
    url = urljoin(base, path)

    # Get DART_API_KEY
    if api_key is None:
        api_key = get_api_key()

    # Set payload
    payload = {
        'crtfc_key': api_key,
        'corp_code': corp_code,
        'bsns_year': bsns_year,
        'reprt_code': reprt_code,
        'bgn_de': bgn_de,
        'end_de': end_de,
        'fs_div': fs_div,
        'sj_div': sj_div,
    }

    payload = {k: v for k, v in payload.items() if v is not None}

    # Request Data
    resp = request.get(url=url, payload=payload)

    # Convert Response to json
    dataset = resp.json()

    # Status Code Check
    check_status(**dataset)
    return dataset

import pytest
from dart_fss.fs_search import *
from dart_fss.errors import NotFoundConsolidated

from .test_crp import crp_list

def test_str_to_float_number():
    actual = str_to_float(1.0)
    expected = 1.0
    assert actual == expected


def test_str_to_float_raise_value_error():
    with pytest.raises(ValueError):
        _ = str_to_float([1, 2])


def test_extract_date_from_header():
    from bs4 import BeautifulSoup

    text = '<td>제21(당)기 2018년 01월 01일부터 12월 31일 까지</dt>'
    text = BeautifulSoup(text, 'html.parser')

    date_info = extract_date_from_header(text)
    actaul = None
    if len(date_info) > 0:
        date_info = date_info[0]
        actaul = '-'.join([x.strftime('%Y%m%d') for x in date_info])
    expected = '20180101-20181231'
    assert actaul == expected


def test_raise_NotFoundConsolidated(crp_list):
    crp = crp_list.find_by_name('두원석재')[0]
    with pytest.raises(NotFoundConsolidated):
        crp.get_financial_statement(start_dt='20000101')


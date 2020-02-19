import pytest
from dart_fss.corp import CorpList


@pytest.fixture(scope='session')
def corp_list():
    return CorpList()


def test_find_by_corp_name(corp_list):
    se = corp_list.find_by_corp_name('삼성전자', exactly=True)[0]
    actual = se.corp_code
    expected = '00126380'
    assert actual == expected


def test_find_by_corp_code(corp_list):
    se_corp_code = '00126380'
    se = corp_list.find_by_corp_code(se_corp_code)
    actual = se.corp_code
    expected = '00126380'
    assert actual == expected


def test_find_by_stock_code(corp_list):
    stock_code = '005930'
    se = corp_list.find_by_stock_code(stock_code)
    actual = se.corp_code
    expected = '00126380'
    assert actual == expected


def test_crp_to_dict(corp_list):
    se = corp_list.find_by_corp_name('삼성전자', exactly=True)[0]
    samsung_dict = se.to_dict()
    actual = samsung_dict['stock_code']
    expected = '005930'
    assert actual == expected

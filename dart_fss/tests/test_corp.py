import pytest


@pytest.fixture(scope='session')
def corp_list(dart):
    return dart.get_corp_list()


def test_find_by_corp_name(corp_list):
    se = corp_list.find_by_corp_name('삼성전자', exactly=True)[0]
    actual = se.corp_code
    expected = '00126380'
    assert actual == expected


def test_find_by_corp_name_with_market_type(corp_list):
    res = corp_list.find_by_corp_name('삼성', market='K')
    actual = len(res)
    expected = 2
    assert actual == expected


def test_find_by_product(corp_list):
    res = corp_list.find_by_product('휴대폰')
    actual = len(res)
    expected = 25
    assert actual == expected


def test_find_by_sector(corp_list):
    res = corp_list.find_by_sector(corp_list.sectors[0])
    actual = len(res)
    expected = 19
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


def test_corp_to_dict(corp_list):
    se = corp_list.find_by_corp_name('삼성전자', exactly=True)[0]
    samsung_dict = se.to_dict()
    actual = samsung_dict['stock_code']
    expected = '005930'
    assert actual == expected


def test_corp_load(corp_list):
    se = corp_list.find_by_corp_name('삼성전자', exactly=True)[0]
    se.load()
    actual = se.jurir_no
    expected = '1301110006246'
    assert actual == expected


def test_corp_get_major_shareholder(corp_list):
    se = corp_list.find_by_corp_name('삼성전자', exactly=True)[0]
    sh = se.get_major_shareholder()
    actual = sh.columns
    expected = 'stkqy_irds'
    assert expected in actual


def test_corp_get_executive_shareholder(corp_list):
    se = corp_list.find_by_corp_name('삼성전자', exactly=True)[0]
    sh = se.get_executive_shareholder()
    actual = sh.columns
    expected = 'sp_stock_lmp_cnt'
    assert expected in actual


def test_corp_search_filings(corp_list):
    se = corp_list.find_by_corp_name('삼성전자', exactly=True)[0]
    filings = se.search_filings(bgn_de='20190101', end_de='20190103')
    actual = filings.total_count
    expected = 1
    assert actual == expected


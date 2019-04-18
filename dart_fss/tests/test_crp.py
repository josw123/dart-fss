import pytest
import dart_fss.crp as crp


@pytest.fixture(scope='session')
def crp_list():
    return crp.get_crp_list()


def test_find_by_name(crp_list):
    se = crp_list.find_by_name('삼성전자')[0]
    actual = se.crp_cd
    expected = '005930'
    assert actual == expected


def test_find_by_crp_cd(crp_list):
    se_crp_cd = '005930'
    se = crp_list.find_by_crp_cd(se_crp_cd)
    actual = se.crp_cd
    expected = '005930'
    assert actual == expected


def test_find_by_product(crp_list):
    product = '교환국장비'
    se = crp_list.find_by_product(product)[0]
    actual = se.crp_cd
    expected = '005930'
    assert actual == expected


def test_crp_to_dict(crp_list):
    samsung = crp_list.find_by_name('삼성전자')[0]
    samsung_dict = samsung.to_dict()
    actual = samsung_dict['crp_cd']
    expected = '005930'
    assert actual == expected

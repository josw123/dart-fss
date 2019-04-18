import pytest

from ..markets import get_market_list, get_market_name, get_market_type


def test_get_market_list():
    market_list = get_market_list()
    expected_mkt_list = ['allMkt', 'stockMkt', 'kosdaqMkt', 'konexMkt', 'etcMkt']
    for _, mkt in market_list.items():
        if mkt not in expected_mkt_list:
            pytest.fail('Invalid market type: {}'.format(mkt))


def test_get_market_name():
    actual = get_market_name('kosdaq')
    expected = 'kosdaqMkt'
    assert actual == expected


def test_get_market_type():
    actual = get_market_type(market='etc')
    expected = 'E'
    assert actual == expected


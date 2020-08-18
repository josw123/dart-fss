def test_get_executive_shareholder(dart):
    res = dart.api.shareholder.get_executive_shareholder('00126380')
    actual = res.get('status')
    expected = '000'
    assert actual == expected


def test_get_major_shareholder(dart):
    res = dart.api.shareholder.get_major_shareholder('00126380')
    actual = res.get('status')
    expected = '000'
    assert actual == expected

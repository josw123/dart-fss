def test_get_single_corp(dart):
    res = dart.api.finance.get_single_corp(corp_code='00126380', bsns_year='2018', reprt_code='11011')
    actual = len(res['list'])
    expected = 26
    assert actual == expected


def test_get_multi_corp(dart):
    res = dart.api.finance.get_multi_corp(['00356370', '00334624'], '2018', '11011')
    actual = len(res['list'])
    expected = 52
    assert actual == expected


def test_download_xbrl(dart):
    import tempfile
    with tempfile.TemporaryDirectory() as temp:
        actual = dart.api.finance.download_xbrl(path=temp, rcept_no='20180402005019', reprt_code='11011')
        assert actual is not None


def test_get_single_fs(dart):
    res = dart.api.finance.get_single_fs('00126380', '2018', '11011', 'CFS')
    actual = res.get('status')
    expected = '000'
    assert actual == expected


def test_get_taxonomy(dart):
    res = dart.api.finance.get_taxonomy('BS1')
    actual = res.get('status')
    expected = '000'
    assert actual == expected
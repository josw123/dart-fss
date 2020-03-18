from dart_fss.api import filings


def test_get_corp_code():
    res = filings.get_corp_code()
    actual = res[0].keys()
    expected = ['corp_code', 'corp_name', 'stock_code', 'modify_date']
    for act in actual:
        assert act in expected


def test_get_corp_info():
    se = filings.get_corp_info('00126380')
    actual = se['est_dt']
    expected = '19690113'
    assert actual == expected


def test_download_document():
    import tempfile
    with tempfile.TemporaryDirectory() as path:
        res = filings.download_document(path, '20190401004781')
        assert res is not None


def test_search_filings():
    f = filings.search_filings(corp_code='00126380', bgn_de='20190101', end_de='20190301', last_reprt_at='Y')
    actual = f['total_count']
    expected = 29
    assert actual == expected
def test_get_corp_code(dart):
    res = dart.api.filings.get_corp_code()
    actual = res[0].keys()
    expected = ['corp_code', 'corp_name', 'corp_eng_name', 'stock_code', 'modify_date'] # API UPDATED
    for act in actual:
        assert act in expected


def test_get_corp_info(dart):
    se = dart.api.filings.get_corp_info('00126380')
    actual = se['est_dt']
    expected = '19690113'
    assert actual == expected


def test_download_document(dart):
    import tempfile
    with tempfile.TemporaryDirectory() as path:
        res = dart.api.filings.download_document(path, '20190401004781')
        assert res is not None


def test_search_filings(dart):
    f = dart.api.filings.search_filings(corp_code='00126380', bgn_de='20190101', end_de='20190301', last_reprt_at='Y')
    actual = f['total_count']
    expected = 29
    assert actual == expected
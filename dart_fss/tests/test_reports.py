import pytest

from ..search import search_report_with_cache


@pytest.fixture(scope='module')
def last_report():
    crp_cd = '005930'
    return search_report_with_cache(crp_cd=crp_cd, start_dt='20180101', end_dt='20190101', bsn_tp='a001')[0]


def test_reports(last_report):
    actual = last_report.rcp_no
    expected = '20180402005019'
    assert actual == expected


def test_reports_load_page(last_report):
    page = last_report.load_page(includes="연결재무제표", excludes="주석")[0]
    actual = page.ele_id
    expected = '13'
    assert actual == expected


def test_reports_pages(last_report):
    first_page = last_report[0]
    actual = first_page.ele_id
    expected = 0
    assert actual == expected


def test_reports_to_dict(last_report):
    results = last_report.to_dict()
    actual = results['crp_nm']
    expected = '삼성전자'
    assert actual == expected


def test_reports_xbrl(last_report):
    xbrl_file = last_report.xbrl.filename
    assert xbrl_file is not None


def test_reports_to_file(last_report):
    import os
    import tempfile

    with tempfile.TemporaryDirectory() as path:
        last_report.to_file(path)
        for _, _, files in os.walk(path):
            if len(files) is not len(last_report):
                pytest.fail("Can't save files")


def test_reports_to_file2():
    import os
    import tempfile
    last_report = search_report_with_cache(crp_cd='080440', start_dt='20190419', dsp_tp='b')[0]
    with tempfile.TemporaryDirectory() as path:
        last_report.to_file(path)
        for _, _, files in os.walk(path):
            if len(files) is not len(last_report):
                pytest.fail("Can't save files")







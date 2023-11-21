import pytest


@pytest.fixture(scope='module')
def last_report(dart):
    corp_code = '00126380'
    return dart.search(corp_code=corp_code, bgn_de='20180101', end_de='20190101', pblntf_detail_ty='a001')[0]


def test_reports(last_report):
    actual = last_report.rcp_no
    expected = '20180402005019'
    assert actual == expected


def test_reports_pages(last_report):
    first_page = last_report[0]
    actual = first_page.ele_id
    expected = 1
    assert actual == expected


def test_reports_to_dict(last_report):
    results = last_report.to_dict()
    actual = results['corp_name']
    expected = '삼성전자'
    assert actual == expected


def test_reports_xbrl(last_report):
    xbrl_file = last_report.xbrl.filename
    assert xbrl_file is not None


def test_reports_find_all(last_report):
    query = {
        'includes': '전문가 AND 확인',
        'excludes': '1'
    }
    page = last_report.find_all(**query)['pages'][0]
    actual = page.dcm_no
    expected = '6060273'
    assert actual == expected


def test_reports_to_dict_summary_false(last_report):
    info = last_report.to_dict(summary=False)
    actual = info.get('xbrl')
    expected = '[삼성전자]사업보고서_IFRS(원문XBRL)(2018.04.02).zip'
    assert actual == expected


def test_xbrlviewer(dart):
    corp_code = '00126380'
    report = dart.search(corp_code=corp_code, bgn_de='20230901', end_de='20231231', pblntf_ty='a')[0]
    actual = len(report.to_dict(summary=False)['xbrlviewer'])
    expected = 1

    assert actual == expected
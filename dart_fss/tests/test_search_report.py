import pytest

from dart_fss.filings import search


@pytest.fixture(scope='module')
def annual_reports():
    corp_code = '00126380'
    return search(corp_code=corp_code, bgn_de='20140101', end_de='20190101', pblntf_detail_ty='a001')


def test_search_report_get_page_no(annual_reports):
    actual = annual_reports.page_no
    expected = 1
    assert actual == expected


def test_search_report_get_page_set(annual_reports):
    actual = annual_reports.page_set
    expected = 10
    assert actual == expected


def test_search_report_total_count(annual_reports):
    actual = annual_reports.total_count
    expected = 5
    assert actual == expected


def test_search_report_total_page(annual_reports):
    actual = annual_reports.total_page
    expected = 1
    assert actual == expected


def test_search_report_report_list(annual_reports):
    actual = len(annual_reports.report_list)
    expected = 5
    assert actual == expected


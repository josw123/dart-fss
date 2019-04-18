import pytest

from ..search import search_report


@pytest.fixture(scope='module')
def annual_reports():
    crp_cd = '005930'
    return search_report(crp_cd=crp_cd, start_dt='20140101', end_dt='20190101', bsn_tp='a001')


def test_search_report_get_page_no(annual_reports):
    actual = annual_reports.page_no
    expected = 1
    assert actual == expected


def test_search_report_set_page_no(annual_reports):
    with pytest.raises(ValueError):
        annual_reports.page_no = 2


def test_search_report_get_page_set(annual_reports):
    actual = annual_reports.page_set
    expected = 10
    assert actual == expected


def test_search_report_set_page_set(annual_reports):
    with pytest.raises(ValueError):
        annual_reports.page_set = 0


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


def test_search_report_filter(annual_reports):
    asc_reports = annual_reports.filter(sort='date', series='asc')
    first_report = asc_reports[0]
    actual = first_report.rcp_dt
    expected = '20140331'
    assert actual == expected


def test_search_report_return_dict():
    actual = search_report(start_dt='20190101', end_dt='20190102', dsp_tp='I', return_dict=True)
    assert isinstance(actual, dict)



import pytest

from dart_fss.fs.search import find_all_columns
from ..search import search_report_with_cache

@pytest.fixture(scope='module')
def samsung_xbrl():
    report = search_report_with_cache(crp_cd='005930', start_dt='20180101', end_dt='20190101', bsn_tp='a001')[0]
    return report.xbrl


def test_xbrl_tables(samsung_xbrl):
    expected = 131
    assert len(samsung_xbrl.tables) == expected


def test_xbrl_get_document_information(samsung_xbrl):
    info = samsung_xbrl.get_document_information()
    actual = info.iloc[1][2]
    expected = '사업보고서'
    assert actual == expected


def test_xbrl_get_period_information(samsung_xbrl):
    period = samsung_xbrl.get_period_information()
    actual = period.iloc[1][2]
    expected = '2017-01-01'
    assert actual == expected


def test_xbrl_get_audit_infomation(samsung_xbrl):
    audit = samsung_xbrl.get_audit_information()
    actual = int(audit.iloc[5][3])
    expected = 260295
    assert actual == expected


def test_xbrl_get_entity_information(samsung_xbrl):
    entity = samsung_xbrl.get_entity_information()
    actual = entity.iloc[2][2]
    expected = int(126380)
    assert actual == expected


def test_xbrl_get_entity_address_information(samsung_xbrl):
    address = samsung_xbrl.get_entity_address_information()
    actual = address.iloc[2][2]
    expected = 'http://www.samsung.com/sec/'
    assert actual == expected


def test_xbrl_get_author_information(samsung_xbrl):
    author = samsung_xbrl.get_author_information()
    column = find_all_columns(author, '공시담당자')[0]
    actual = author[column][3]
    expected = '031-277-7227'
    assert actual == expected


def test_xbrl_get_financial_statement_information(samsung_xbrl):
    state = samsung_xbrl.get_financial_statement_information()
    actual = state.iloc[3][2]
    expected = 'D3001'
    assert actual == expected


def test_xbrl_get_financial_statement(samsung_xbrl):
    fs = samsung_xbrl.get_financial_statement()[0]
    actual = fs.code
    expected = 'D210000'
    assert actual == expected


def test_xbrl_to_Dataframe(samsung_xbrl):
    fs = samsung_xbrl.get_financial_statement()[0]
    actual = int(fs.to_DataFrame(show_concept=False, show_class=False, label='연결').iloc[0][2])
    expected = 146982464000000
    assert actual == expected


def test_xbrl_get_value_by_concept_id(samsung_xbrl):
    fs = samsung_xbrl.get_financial_statement()[0]
    data = fs.get_value_by_concept_id('ifrs_CurrentAssets', start_dt='20170101', label='Consolidated')
    actual = data[('20171231', ('Consolidated',))]
    expected = 146982464000000
    assert actual == expected


import pytest

from ..search import search_report_with_cache
from ..xbrl import get_xbrl_from_website


def test_get_xbrl_from_website():
    import re
    url = 'http://dart.fss.or.kr/pdf/download/ifrs.do?rcp_no=20180402005019&dcm_no=6060273&lang=ko'
    xbrl = get_xbrl_from_website(url=url)[0]
    assert re.search(r'00126380_2011-04-30.xbrl', xbrl.filename)


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
    actual = author['[2017-01-01,2017-12-31]공시담당자'][3]
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
    actual = int(fs.to_Dataframe(show_concept=False, show_class=False, title='연결').iloc[0][2])
    expected = 146982464000000
    assert actual == expected


def test_xbrl_get_value_by_concept_id(samsung_xbrl):
    fs = samsung_xbrl.get_financial_statement()[0]
    data = fs.get_value_by_concept_id('ifrs_CurrentAssets', start_date='2017-01-01', cls_type='con')
    _, actual = data.popitem()
    expected = 146982464000000
    assert actual == expected


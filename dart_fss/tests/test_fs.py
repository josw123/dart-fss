import pytest
from dart_fss.fs.extract import find_all_columns

from .test_case.crp_case import test_crp_list
from .test_corp import corp_list


@pytest.mark.slow
@pytest.mark.parametrize("corp", test_crp_list)
def test_crp_financial_statement(corp, corp_list):
    corp.set_corp_list(corp_list)
    corp.run_test()


@pytest.fixture(scope='session')
def fs_report(corp_list):
    # 00164779: SK하이닉스
    skhynix = corp_list.find_by_corp_code('00164779')
    return skhynix.extract_fs(bgn_de='20180101')


def test_fs_class_false(fs_report):
    df = fs_report.show('bs', show_class=False)
    columns = find_all_columns(df, 'class')
    actual = len(columns)
    expected = 0
    assert actual == expected


def test_fs_concept_false(fs_report):
    df = fs_report.show('bs', show_concept=False)
    columns = find_all_columns(df, 'concept')
    actual = len(columns)
    expected = 0
    assert actual == expected


def test_fs_show_depth(fs_report):
    df = fs_report.show('bs', show_depth=1)
    columns = find_all_columns(df, 'class')
    actual = len(columns)
    expected = 2
    assert actual == expected


def test_fs_to_dict(fs_report):
    info = fs_report.to_dict()
    actual = info['corp_code']
    expected = '00164779'
    assert actual == expected


def test_fs_to_save(fs_report):
    import os
    import tempfile
    with tempfile.TemporaryDirectory() as path:
        file_path = fs_report.save(path=path)
        actual = os.path.isfile(file_path)
    expected = True
    assert actual == expected


def test_fs_load(fs_report):
    import tempfile
    with tempfile.TemporaryDirectory() as path:
        expected = fs_report.info
        file_path = fs_report.save(path=path)
        loaded_report = fs_report.load(file_path)
    assert loaded_report.info == expected


@pytest.fixture
def test_cases_for_xbrl():
    return [
        {
            "stock_code": "051310",
            "date": "20120814",
            "report_tp": "half",
            "fs_tp": "cis",
            "expected": 29
        },
        {
            "stock_code": "000880",
            "date": "20171114",
            "report_tp": "quarter",
            "fs_tp": "cis",
            "expected": 19
        },
        {
            "stock_code": "007280",
            "date": "20130515",
            "report_tp": "quarter",
            "fs_tp": "bs",
            "expected": 52
        },
        {
            "stock_code": "011080",
            "date": "20121113",
            "report_tp": "quarter",
            "fs_tp": "cf",
            "expected": 190
        },
        {
            "stock_code": "016170",
            "date": "20171114",
            "report_tp": "quarter",
            "fs_tp": "bs",
            "expected": 34
        },
        {
            "stock_code": "016170",
            "date": "20171114",
            "report_tp": "quarter",
            "fs_tp": "cf",
            "expected": 66
        },
        {
            "stock_code": "038320",
            "date": "20120515",
            "report_tp": "quarter",
            "fs_tp": "cf",
            "expected": 135
        },
        {
            "stock_code": "038320",
            "date": "20120824",
            "report_tp": "half",
            "fs_tp": "cf",
            "expected": 145
        },
        {
            "stock_code": "009240",
            "date": "20130401",
            "report_tp": "annual",
            "fs_tp": "bs",
            "expected": 35
        },
    ]


@pytest.fixture(scope='session')
def test_extract_fs(test_cases_for_xbrl, corp_list):
    for test_case in test_cases_for_xbrl:
        corp = corp_list.find_by_stock_code(
            test_case["stock_code"], include_delisting=True
        )
        fs = corp.extract_fs(
            bgn_de=test_case["date"],
            end_de=test_case["date"],
            report_tp=[test_case["report_tp"]],
            separate=True,
        )
        actual = fs[test_case["fs_tp"]].shape[0]
        expected = test_case["expected"]
        assert actual == expected, (
            f"Failed for {test_case['stock_code']} "
            f"on {test_case['date']} "
            f"with report type {test_case['report_tp']} "
            f"and financial statement type {test_case['fs_tp']}. "
            f"Expected {expected}, but got {actual}."
        )
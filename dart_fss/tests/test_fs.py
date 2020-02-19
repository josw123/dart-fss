import pytest
from dart_fss.fs.extract import find_all_columns

from .test_case.crp_case import test_crp_list
from .test_corp import corp_list

@pytest.mark.parametrize("corp", test_crp_list)
def test_crp_financial_statement(corp):
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
    expected = '000660'
    assert actual == expected


def test_fs_to_save(fs_report):
    import os
    import tempfile
    with tempfile.TemporaryDirectory() as path:
        file_path = fs_report.save(path=path)
        actual = os.path.isfile(file_path)
    expected = True
    assert actual == expected

import pytest
from dart_fss.fs.search import find_all_columns

from .test_case.crp_case import test_crp_list

@pytest.mark.parametrize("crp", test_crp_list)
def test_crp_financial_statement(crp):
    crp.run_test()


@pytest.fixture(scope='session')
def fs_report(crp_list):
    skhynix = crp_list.find_by_name('하이닉스')[0]
    return skhynix.get_financial_statement(start_dt='20180101')


def test_fs_class_false(fs_report):
    df = fs_report.show('fs', show_class=False)
    columns = find_all_columns(df, 'class')
    actual = len(columns)
    expected = 0
    assert actual == expected


def test_fs_concept_false(fs_report):
    df = fs_report.show('fs', show_concept=False)
    columns = find_all_columns(df, 'concept')
    actual = len(columns)
    expected = 0
    assert actual == expected


def test_fs_show_depth(fs_report):
    df = fs_report.show('fs', show_depth=1)
    columns = find_all_columns(df, 'class')
    actual = len(columns)
    expected = 2
    assert actual == expected


def test_fs_to_dict(fs_report):
    info = fs_report.to_dict()
    actual = info['crp_cd']
    expected = '000660'
    assert  actual == expected


def test_fs_to_save(fs_report):
    import os
    import tempfile
    with tempfile.TemporaryDirectory() as path:
        file_path = fs_report.save(path=path)
        actual = os.path.isfile(file_path)
    expected = True
    assert actual == expected

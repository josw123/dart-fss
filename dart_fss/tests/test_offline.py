import copy
import pickle

import numpy as np
import pandas as pd

from dart_fss.corp import Corp
from dart_fss.filings.reports import Report
from dart_fss.fs.fs import FinancialStatement
from dart_fss.utils.dataframe import dataframe_astype
from dart_fss.utils.regex import str_to_regex


def test_dataframe_astype_keeps_sign():
    df = pd.DataFrame({'a': ['1,000', '-2,500', '0'], 'b': ['1.5', '-0.25', '3']})
    df = dataframe_astype(df, [('a', int), ('b', float)])
    assert df['a'].tolist() == [1000, -2500, 0]
    assert df['b'].tolist() == [1.5, -0.25, 3.0]


def test_dataframe_astype_keeps_original_on_failure():
    df = pd.DataFrame({'a': ['3,318,230', '-']})
    df = dataframe_astype(df, [('a', int)])
    assert df['a'].tolist() == ['3,318,230', '-']


def test_report_copy_and_pickle():
    report = Report(rcept_no='20190401004781')
    for clone in (copy.copy(report), copy.deepcopy(report), pickle.loads(pickle.dumps(report))):
        assert clone.rcept_no == '20190401004781'


def test_corp_copy_and_pickle():
    corp = Corp(corp_code='00126380', corp_name='삼성전자')
    for clone in (copy.copy(corp), copy.deepcopy(corp), pickle.loads(pickle.dumps(corp))):
        assert clone.corp_name == '삼성전자'


def test_str_to_regex_cached():
    assert str_to_regex('A AND B') is str_to_regex('A AND B')
    assert str_to_regex('A AND B').search('B A')


def test_fs_show_depth_with_nan():
    title = '[D210000] 재무상태표'
    columns = pd.MultiIndex.from_tuples([(title, 'concept_id'), (title, 'label_ko'), (title, 'class0'),
                                         (title, 'class1'), (title, 'class2'), (title, '20201231')])
    df = pd.DataFrame([
        ['c1', '자산', '자산', np.nan, np.nan, 100.0],
        ['c2', '유동자산', '자산', '유동자산', np.nan, 60.0],
        ['c3', '현금', '자산', '유동자산', '현금', 10.0],
    ], columns=columns)
    fs = FinancialStatement({'bs': df}, {'bs': None}, {})
    actual = fs.show('bs', show_depth=1)
    assert actual[(title, 'concept_id')].tolist() == ['c1', 'c2']


def test_fs_result_cache(tmp_path):
    from types import SimpleNamespace
    from dart_fss.fs.extract import _ResultCache

    cache = _ResultCache(str(tmp_path))
    report = SimpleNamespace(rcept_no='20190401004781')
    option = dict(fs_tp=('bs',), separate=False, lang='ko', separator=True)
    fs_df = {'bs': pd.DataFrame({'a': [1.0, np.nan]})}

    assert cache.load(report, option) is None
    cache.save(report, option, fs_df)
    assert cache.exists(report, option)
    pd.testing.assert_frame_equal(cache.load(report, option)['bs'], fs_df['bs'])
    # 옵션이 다르면 별도 캐시
    assert cache.load(report, dict(option, separate=True)) is None
    assert cache.load(report, dict(option, dataset='web')) is None


def test_ordered_column_helpers():
    from dart_fss.fs.extract import ordered_columns, ordered_intersection

    a = pd.MultiIndex.from_tuples([('20201231', 'x'), ('20191231', 'x'), ('20181231', 'x'), ('20191231', 'x')])
    b = pd.MultiIndex.from_tuples([('20181231', 'x'), ('20201231', 'x')])
    assert ordered_columns(a) == [('20201231', 'x'), ('20191231', 'x'), ('20181231', 'x')]
    assert ordered_intersection(a, b) == [('20201231', 'x'), ('20181231', 'x')]
    assert ordered_columns(None) == [] and ordered_intersection(None, b) == []

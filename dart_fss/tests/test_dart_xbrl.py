from datetime import datetime

import pytest

from dart_fss.xbrl.dart_xbrl import DartXbrl


def _make_xbrl(
    tables=None,
    consolidated_financial_statement=None,
    separate_financial_statement=None,
    consolidated_income_statement=None,
    separate_income_statement=None,
    consolidated_changes_in_equity=None,
    separate_changes_in_equity=None,
    consolidated_cash_flows=None,
    separate_cash_flows=None,
):
    xbrl = DartXbrl.__new__(DartXbrl)
    xbrl._tables = tables
    xbrl.get_financial_statement = lambda separate=False: (
        separate_financial_statement if separate else consolidated_financial_statement
    )
    xbrl.get_income_statement = lambda separate=False: (
        separate_income_statement if separate else consolidated_income_statement
    )
    xbrl.get_changes_in_equity = lambda separate=False: (
        separate_changes_in_equity if separate else consolidated_changes_in_equity
    )
    xbrl.get_cash_flows = lambda separate=False: (
        separate_cash_flows if separate else consolidated_cash_flows
    )
    return xbrl


def test_is_empty_returns_true_without_tables():
    xbrl = _make_xbrl(tables=[])

    assert xbrl.is_empty() is True


def test_is_empty_returns_true_without_financial_statement_tables():
    xbrl = _make_xbrl(tables=[object()])

    assert xbrl.is_empty() is True


def test_is_empty_returns_false_for_consolidated_only_statement():
    xbrl = _make_xbrl(
        tables=[object()],
        consolidated_financial_statement=[object()],
    )

    assert xbrl.is_empty() is False


def test_is_empty_returns_false_for_separate_only_statement():
    xbrl = _make_xbrl(
        tables=[object()],
        separate_financial_statement=[object()],
    )

    assert xbrl.is_empty() is False


class _FakeTable:
    def __init__(self, code, definition, concept_values=None, cls=None):
        self.code = code
        self.definition = definition
        self._concept_values = concept_values or {}
        self.cls = cls if cls is not None else []

    def get_value_by_concept_id(self, concept_id, **kwargs):
        return self._concept_values.get(concept_id, {})


def _make_xbrl_with_tables(tables):
    xbrl = DartXbrl.__new__(DartXbrl)
    xbrl._tables = tables
    return xbrl


def _info_table(concept_values=None, cls=None):
    return _FakeTable(
        'D999007',
        '[D999007] 보고서정보 - 재무제표 정보 | Financial Statement Information',
        concept_values=concept_values,
        cls=cls,
    )


_BS_CONSOLIDATED = _FakeTable(
    'D210000',
    '[D210000] 재무상태표, 유동/비유동법 - 연결 | Statement of financial position, '
    'current/non-current - Consolidated financial statements')
_BS_SEPARATE = _FakeTable(
    'D210005',
    '[D210005] 재무상태표, 유동/비유동법 - 별도 | Statement of financial position, '
    'current/non-current - Separated financial statements')
_IS_CONSOLIDATED = _FakeTable(
    'D310000',
    '[D310000] 손익계산서, 기능별 분류 - 연결 | Income statement, by function of expense '
    '- Consolidated financial statements')
_CIS_CONSOLIDATED = _FakeTable(
    'D410000',
    '[D410000] 포괄손익계산서 - 연결 | Statement of comprehensive income '
    '- Consolidated financial statements')
_SINGLE_CIS_CONSOLIDATED = _FakeTable(
    'D432410',
    '[D432410] 단일 포괄손익계산서, 기능별 분류 - 연결 | Statement of comprehensive income, '
    'single statement, by function of expense - Consolidated financial statements')
_CIE_CONSOLIDATED = _FakeTable(
    'D610000',
    '[D610000] 자본변동표 - 연결 | Statement of changes in equity '
    '- Consolidated financial statements')
_CF_CONSOLIDATED = _FakeTable(
    'D520000',
    '[D520000] 현금흐름표, 간접법 - 연결 | Statement of cash flows, indirect method '
    '- Consolidated financial statements')
_CF_SEPARATE = _FakeTable(
    'D520005',
    '[D520005] 현금흐름표, 간접법 - 별도 | Statement of cash flows, indirect method '
    '- Separated financial statements')
_CF_NOTE_CONSOLIDATED = _FakeTable(
    'D851100',
    '[D851100] 35. 현금흐름표 - 연결 | 35. Cash flow statement '
    '- Consolidated financial statements')

_BS_CONCEPT = 'dart-gcd_StatementOfFinancialPosition'
_CONSOLIDATED_KEY = ('20241231', ('Consolidated financial statements',))
_SEPARATE_KEY = ('20241231', ('Separated financial statements',))


def test_get_statement_normal_path_unchanged():
    info = _info_table(concept_values={_BS_CONCEPT: {_CONSOLIDATED_KEY: 'D1001'}})
    xbrl = _make_xbrl_with_tables([_BS_CONSOLIDATED, info])

    tables = xbrl.get_financial_statement(separate=False)
    assert [t.code for t in tables] == ['D210000']


def test_get_statement_fallback_when_d999007_empty():
    xbrl = _make_xbrl_with_tables([_BS_CONSOLIDATED, _BS_SEPARATE, _info_table()])

    consolidated = xbrl.get_financial_statement(separate=False)
    assert [t.code for t in consolidated] == ['D210000']

    separate = xbrl.get_financial_statement(separate=True)
    assert [t.code for t in separate] == ['D210005']


def test_get_statement_fallback_filters_annotation_roles():
    xbrl = _make_xbrl_with_tables(
        [_CF_CONSOLIDATED, _CF_NOTE_CONSOLIDATED, _info_table()])

    tables = xbrl.get_cash_flows(separate=False)
    assert [t.code for t in tables] == ['D520000']


def test_get_statement_fallback_none_when_separate_only():
    xbrl = _make_xbrl_with_tables([_BS_SEPARATE, _info_table()])

    assert xbrl.get_financial_statement(separate=False) is None


def test_get_statement_no_fallback_when_d999007_says_separate_only():
    info = _info_table(concept_values={_BS_CONCEPT: {_SEPARATE_KEY: 'D1001'}})
    xbrl = _make_xbrl_with_tables([_BS_CONSOLIDATED, info])

    assert xbrl.get_financial_statement(separate=False) is None


def test_get_statement_fallback_income_statement_order():
    xbrl = _make_xbrl_with_tables(
        [_IS_CONSOLIDATED, _CIS_CONSOLIDATED, _info_table()])

    tables = xbrl.get_income_statement(separate=False)
    assert [t.code for t in tables] == ['D310000', 'D410000']


def test_get_statement_fallback_single_comprehensive_income():
    xbrl = _make_xbrl_with_tables([_SINGLE_CIS_CONSOLIDATED, _info_table()])

    tables = xbrl.get_income_statement(separate=False)
    assert [t.code for t in tables] == ['D432410']


def test_get_statement_keyerror_path_filters_annotation():
    info = _info_table(
        concept_values={'dart-gcd_StatementOfCashFlows': {_CONSOLIDATED_KEY: 'D9999'}})
    xbrl = _make_xbrl_with_tables([_CF_CONSOLIDATED, _CF_NOTE_CONSOLIDATED, info])

    tables = xbrl.get_cash_flows(separate=False)
    assert [t.code for t in tables] == ['D520000']


def test_get_statement_none_when_d999007_missing():
    xbrl = _make_xbrl_with_tables([_BS_CONSOLIDATED])

    assert xbrl.get_financial_statement(separate=False) is None


def test_exist_consolidated_fallback_true():
    xbrl = _make_xbrl_with_tables([_BS_CONSOLIDATED, _BS_SEPARATE, _info_table()])

    assert xbrl.exist_consolidated() is True


def test_exist_consolidated_fallback_false():
    xbrl = _make_xbrl_with_tables([_BS_SEPARATE, _info_table()])

    assert xbrl.exist_consolidated() is False


def test_exist_consolidated_raises_when_missing():
    xbrl = _make_xbrl_with_tables([_BS_CONSOLIDATED])

    with pytest.raises(ValueError):
        xbrl.exist_consolidated()


def test_exist_consolidated_normal_path():
    cls = [{
        'cls_id': 'ctx1',
        'instant_datetime': datetime(2024, 12, 31),
        'start_datetime': None,
        'end_datetime': None,
        'label': {'dim': {'ko': '연결재무제표', 'en': 'Consolidated financial statements'}},
    }]
    xbrl = _make_xbrl_with_tables([_BS_CONSOLIDATED, _info_table(cls=cls)])

    assert xbrl.exist_consolidated() is True


def test_is_empty_false_for_empty_d999007_with_statement_roles():
    xbrl = _make_xbrl_with_tables([
        _BS_CONSOLIDATED, _BS_SEPARATE,
        _SINGLE_CIS_CONSOLIDATED, _CIE_CONSOLIDATED,
        _CF_CONSOLIDATED, _CF_SEPARATE,
        _info_table(),
    ])

    assert xbrl.is_empty() is False

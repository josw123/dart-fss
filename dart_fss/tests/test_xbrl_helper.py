import math
from datetime import datetime
from types import SimpleNamespace

from dart_fss.xbrl.helper import (get_value_from_dataset,
                                  consolidated_code_to_role_number,
                                  get_statement_role_numbers)


def _make_fact(concept_id, value, decimals='0'):
    return SimpleNamespace(
        concept=SimpleNamespace(id=concept_id),
        value=value,
        decimals=decimals,
    )


def _make_cls(cls_id, instant='20250930'):
    return {
        'cls_id': cls_id,
        'instant_datetime': datetime.strptime(instant, '%Y%m%d'),
        'start_datetime': None,
        'end_datetime': None,
        'label': {'ko': {'ko': '연결', 'en': 'Consolidated'}},
    }


def test_string_value_is_preserved():
    concept_id = 'ifrs-full_RestrictedCash'
    text = '사용제한 예치금에는 현금및현금성자산의 정의를 충족하는 지준예치금 등이 제외되어 있습니다.'
    cls = _make_cls('ctx_2025Q3')
    dataset = {'ctx_2025Q3': [_make_fact(concept_id, text)]}

    result = get_value_from_dataset(cls, dataset, concept_id)
    assert result == [text]


def test_number_wins_over_text_on_duplicate_title():
    concept_id = 'ifrs-full_Cash'
    cls_a = _make_cls('ctx_a')
    cls_b = _make_cls('ctx_b')
    dataset = {
        'ctx_a': [_make_fact(concept_id, '사용제한 예치금')],
        'ctx_b': [_make_fact(concept_id, '1234567890')],
    }

    result = get_value_from_dataset([cls_a, cls_b], dataset, concept_id)
    assert result == [1234567890.0]


def test_text_after_number_no_typeerror():
    """Regression for #172 and the 하나금융지주 2025 Q3 case: a text fact arriving
    after a numeric fact for the same title used to crash math.isnan() on line 179."""
    concept_id = 'ifrs-full_Cash'
    cls_a = _make_cls('ctx_a')
    cls_b = _make_cls('ctx_b')
    dataset = {
        'ctx_a': [_make_fact(concept_id, '1234567890')],
        'ctx_b': [_make_fact(concept_id, '사용제한 예치금')],
    }

    result = get_value_from_dataset([cls_a, cls_b], dataset, concept_id)
    assert result == [1234567890.0]


def test_numeric_string_still_parses():
    concept_id = 'ifrs-full_Cash'
    cls = _make_cls('ctx_x')
    dataset = {'ctx_x': [_make_fact(concept_id, '987654321')]}
    assert get_value_from_dataset(cls, dataset, concept_id) == [987654321.0]


def test_none_value_returns_nan():
    concept_id = 'ifrs-full_Cash'
    cls = _make_cls('ctx_n')
    dataset = {'ctx_n': [_make_fact(concept_id, None)]}
    result = get_value_from_dataset(cls, dataset, concept_id)
    assert len(result) == 1 and math.isnan(result[0])


def test_currency_unit_branch_safe_on_text():
    concept_id = 'ifrs-full_Cash'
    text = '사용제한 예치금'
    cls = _make_cls('ctx_u')
    dataset = {'ctx_u': [_make_fact(concept_id, text, decimals=None)]}
    result = get_value_from_dataset(cls, dataset, concept_id, label_ko='현금및현금성자산(단위:원)')
    assert result == [text]


def test_consolidated_code_to_role_number_regression():
    assert consolidated_code_to_role_number('D2005') == ['D310000', 'D410000']
    assert consolidated_code_to_role_number('D2005', separate=True) == ['D310005', 'D410005']
    assert consolidated_code_to_role_number('D1001') == ['D210000']
    assert consolidated_code_to_role_number('D1001', separate=True) == ['D210005']


def test_get_statement_role_numbers():
    consolidated = get_statement_role_numbers()
    assert 'D210000' in consolidated
    assert 'D520000' in consolidated
    assert 'D851100' not in consolidated
    assert 'D520005' not in consolidated

    separated = get_statement_role_numbers(separate=True)
    assert 'D520005' in separated
    assert 'D520000' not in separated

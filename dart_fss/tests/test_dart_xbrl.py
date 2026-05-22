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

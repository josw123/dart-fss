import pytest

from .test_crp import crp_list
from ..errors import DartAPIError, NotFoundConsolidated, check_err_code


def test_check_err_code():
    with pytest.raises(DartAPIError, match=r'.*crp_cd.*'):
        err_code = {
            'err_code': 100,
            'err_msg': 'crp_cd 없는 경우 검색기간은 3개월만 가능'
        }
        check_err_code(**err_code)


def test_check_err_code_900():
    with pytest.raises(DartAPIError, match=r'.*Invalid.*'):
        err_code = {
            'err_code': 123,
            'err_msg': 'Invalid Error'
        }
        check_err_code(**err_code)


def test_not_found_consolidated(crp_list):
    with pytest.raises(NotFoundConsolidated):
        crp = crp_list.find_by_name('모두투어리츠')[0]
        crp.get_financial_statement(start_dt='20180101')
import pytest

from ..errors import DartException, check_err_code


def test_check_err_code():
    with pytest.raises(DartException, match=r'.*crp_cd.*'):
        err_code = {
            'err_code': 100,
            'err_msg': 'crp_cd 없는 경우 검색기간은 3개월만 가능'
        }
        check_err_code(**err_code)


def test_check_err_code_900():
    with pytest.raises(DartException, match=r'.*Invalid.*'):
        err_code = {
            'err_code': 123,
            'err_msg': 'Invalid Error'
        }
        check_err_code(**err_code)
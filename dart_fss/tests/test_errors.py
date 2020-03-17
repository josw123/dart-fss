import pytest

from dart_fss.errors import *
from .test_corp import corp_list


def test_check_status():
    ret_code = {
        'status': '000',
        'message': '정상'
    }
    check_status(**ret_code)


def test_errors():
    errors = [
        ('010', APIKeyError),
        ('011', TemporaryLocked),
        ('013', NoDataReceived),
        ('020', OverQueryLimit),
        ('100', InvalidField),
        ('800', ServiceClose),
        ('900', UnknownError),
    ]
    for status, err in errors:
        with pytest.raises(err):
            err_code = {
                'status': status,
            }
            check_status(**err_code)


def test_not_found_consolidated(corp_list):
    with pytest.raises(NotFoundConsolidated):
        crp = corp_list.find_by_corp_name('모두투어리츠')[0]
        crp.extract_fs(bgn_de='20180101')
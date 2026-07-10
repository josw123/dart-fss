import pytest
from .test_corp import corp_list

def test_check_status(dart):
    ret_code = {
        'status': '000',
        'message': '정상'
    }
    dart.errors.check_status(**ret_code)


def test_errors(dart):
    errors = [
        ('010', dart.errors.APIKeyError),
        ('011', dart.errors.TemporaryLocked),
        ('013', dart.errors.NoDataReceived),
        ('020', dart.errors.OverQueryLimit),
        ('100', dart.errors.InvalidField),
        ('800', dart.errors.ServiceClose),
        ('900', dart.errors.UnknownError),
    ]
    for status, err in errors:
        with pytest.raises(err):
            err_code = {
                'status': status,
            }
            dart.errors.check_status(**err_code)


def test_not_found_consolidated(dart, corp_list):
    with pytest.raises(dart.errors.NotFoundConsolidated):
        # 구 모두투어리츠: 사명 변경/상장폐지와 무관하도록 corp_code로 조회
        crp = corp_list.find_by_corp_code('01035289')
        crp.extract_fs(bgn_de='20180101', end_de='20190101', skip_error=False)

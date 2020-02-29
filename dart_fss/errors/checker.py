# -*- coding: utf-8 -*-
from dart_fss.errors.errors import (APIKeyError, TemporaryLocked, NoDataReceived,
                                    OverQueryLimit, InvalidField, ServiceClose, UnknownError)


def check_error(status):
    errors = {
        '000': None,
        '010': APIKeyError,
        '011': TemporaryLocked,
        '013': NoDataReceived,
        '020': OverQueryLimit,
        '100': InvalidField,
        '800': ServiceClose,
        '900': UnknownError,
    }
    return errors.get(status, UnknownError)


def check_status(**kwargs):
    """
    Open DART의 응답 결과중 status 값을 체크하는 함수
    Parameters
    ----------
    kwargs: dict
        DART 서버에서 전달받은 값

    Raises
    ------
    APIKeyError
        등록되지 않은 API 키에 의해 발생하는 오류
    TemporaryLocked
        오픈 API에 등록 되었으나, 일시적으로 사용 중지된 키에 의해 발생하는 오류
    OverQueryLimit
        요청 제한을 초과하였을때 발생하는 오류
    InvalidField
        요청한 필드에 부적절한 값이 있는 경우 발생하는 오류
    ServiceClose
        원할한 공시서비스를 위해 오픈 API 서비스가 중지 되었을때 발생하는 오류
    UnknownError
        정의되지 않은 오류
    """
    status = kwargs.get('status')
    err = check_error(status)
    if err is not None:
        msg = kwargs.get('message')
        raise err(msg)

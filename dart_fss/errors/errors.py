# -*- coding: utf-8 -*-
class APIKeyError(ValueError):
    """
    등록되지 않은 API 키에 의해 발생하는 오류
    """
    def __init__(self, msg='Unregistered API key'):
        super().__init__(msg)


class TemporaryLocked(RuntimeError):
    """
    오픈 API에 등록 되었으나, 일시적으로 사용 중지된 키에 의해 발생하는 오류
    """
    def __init__(self, msg='Temporarily locked'):
        super().__init__(msg)


class NoDataReceived(ValueError):
    """
    조회된 데이터가 없을때 발생하는 오류
    """
    def __init__(self, msg='No data received'):
        super().__init__(msg)


class OverQueryLimit(RuntimeError):
    """
    요청 제한을 초과하였을때 발생하는 오류
    """
    def __init__(self, msg='Over query limit'):
        super().__init__(msg)


class InvalidField(ValueError):
    """
    요청한 필드에 부적절한 값이 있는 경우 발생하는 오류
    """
    def __init__(self, msg='Invalid field'):
        super().__init__(msg)


class ServiceClose(RuntimeError):
    """
    원할한 공시서비스를 위해 오픈 API 서비스가 중지 되었을때 발생하는 오류
    """
    def __init__(self, msg='Open API was closed for web service'):
        super().__init__(msg)


class UnknownError(RuntimeError):
    """
    정의되지 않은 오류
    """
    def __init__(self, msg='Unknown error'):
        super().__init__(msg)


class NotFoundConsolidated(ValueError):
    """
    연결재무제표가 없을때 발생하는 오류
    """
    def __init__(self, err_msg='Could not find consolidated financial statements'):
        super().__init__(err_msg)

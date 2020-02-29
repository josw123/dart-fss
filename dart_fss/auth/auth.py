# -*- coding: utf-8 -*-
import os

from dart_fss.utils import Singleton, request
from dart_fss.errors import check_status


def set_api_key(api_key: str) -> str:
    """ Set Open DART API KEY

    Parameters
    ----------
    api_key: str
        Open DART API KEY
    Returns
    -------
    str
        설정된 API KEY
    """
    DartAuth().api_key = api_key
    auth = DartAuth()
    return auth.api_key


def get_api_key() -> str:
    """ Get Open DART API KEY

    Returns
    -------
    str
        DART_API_KEY
    """
    return DartAuth().api_key


class DartAuth(object, metaclass=Singleton):
    """DART 오픈 API 인증키 관련 클래스.

    DART 오픈 API 사용을 사용되는 인증키를 관리하는 클래스입니다.
    API 인증키를 직접 설정하는 방법과 환경 변수를 통해 설정하는 방법이 있습니다.
    환경변수의 변수명은 DART_API_KEY 입니다.

    Note
    ----
    DART 인증키 발급은 https://opendart.fss.or.kr/ 를 참고하십시오.

    Attributes
    ----------
    api_key: str
         DART 인증키

    """

    def __init__(self, api_key=None):
        """ api_key 초기화 메서드

        api_key 초기값이 없을시 환경변수 DART_API_KEY 확인

        Parameters
        ----------
        api_key: str, optional
            DART API KEY 정보
        """
        super().__init__()
        self.__api_key = None
        if api_key is None:
            api_key = os.getenv('DART_API_KEY')
        if api_key:
            self.api_key = api_key

    @property
    def api_key(self) -> str:
        """ str: Dart 인증키 """
        if self.__api_key is None:
            raise ValueError('Unauthorized')
        return self.__api_key

    @api_key.setter
    def api_key(self, api_key: str) -> None:
        if not isinstance(api_key, str):
            raise ValueError('The Dart Api key must be provided through the api_key variable')

        # 기업개황 테스트
        url = 'https://opendart.fss.or.kr/api/company.json'
        # 요청인자
        # crtfc_key: API 인증키
        # corp_code: 공시대항회사 고유번호 /  00126380 삼성전자
        payload = {'crtfc_key': api_key, 'corp_code': '00126380'}

        resp = request.get(url=url, payload=payload)
        data = resp.json()

        check_status(**data)
        self.__api_key = api_key

    def __repr__(self) -> str:
        return 'API key: {}'.format(self.api_key)


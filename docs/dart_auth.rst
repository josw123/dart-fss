Open DART Auth
==================================

- DART-FSS 라이브러리 사용을 위해서는 Open DART API Key 설정 필요

Open DART API Key 신청
----------------------------------
-   `OPEN DART API 신청 <https://opendart.fss.or.kr/>`_


API Key 설정
----------------------------------

.. note:: 환경 변수 설정 또는 set_api_key 사용을 통해 API Key 설정 필요

환경변수 설정
''''''''''''''''''''''''''''''''''
환경 변수 DART_API_KEY 설정을 통한 API Key 설정

- 변수명: DART_API_KEY
- 변수값: Open DART에서 발급받은 API KEY

라이브러리 함수 사용
''''''''''''''''''''''''''''''''''
DART-FSS 라이브러리 함수를 이용한 API Key 설정

..  code-block:: python

    import dart_fss as dart

    # Open DART API KEY 설정
    api_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    dart.set_api_key(api_key=api_key)


API Key 확인
----------------------------------
설정된 Open DART API Key 확인

.. code-block:: python

    import dart_fss as dart

    api_key = dart.get_api_key()


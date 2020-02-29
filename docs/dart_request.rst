Request 설정
=================================

DART-FSS 라이브러리에서 사용하는 Request 관련 설정 방법입니다.

..  note:: dart_fss.utils.request 로 접근이 가능하며, 아래의 Singleton Class로 구현되어 있습니다.

request
'''''''''''''

- DART-FSS 라이브러리 Request 요청을 위한 클래스 (Singleton)
- 접근 방법은 Example 참고

.. autoclass:: dart_fss.utils.request.Request
    :members:

Example
'''''''''''''

..  code-block:: python

    import dart_fss as dart

    # DART_FSS Request Delay 0.7s로 변경
    dart.utils.request.set_delay(0.7)

    # 프록시 설정
    proxies = {'http': 'http://xxxxxxxxx.xxx','https': 'https://xxxxxxxxx.xxx'}
    dart.utils.request.set_proxies(proxies)

    # User-Agent 강제 변경
    dart.utils.request.update_user_agent(force=True)

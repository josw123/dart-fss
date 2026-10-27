DART-FSS
===========================

..  image:: https://img.shields.io/pypi/v/dart-fss.svg
    :target: https://pypi.org/project/dart-fss/
..  image:: https://img.shields.io/pypi/pyversions/dart-fss.svg
    :target: https://pypi.org/project/dart-fss/
..  image:: https://img.shields.io/pypi/l/dart-fss.svg
    :target: https://github.com/josw123/dart-fss/blob/master/LICENSE

대한민국 금융감독원에서 운영하는 다트(`DART <https://dart.fss.or.kr>`_) 사이트 크롤링 및 재무제표 추출을 위한 라이브러리

Installation
---------------------------

-   Python 3.9 이상 지원

..  code::

    pip install -U dart-fss

Open DART API Key 신청
---------------------------
-   `OPEN DART API 신청 <https://opendart.fss.or.kr/>`_

Quick Starts
----------------------
..  code-block:: python

    import dart_fss as dart

    # Open DART API KEY 설정
    api_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    dart.set_api_key(api_key=api_key)

    # DART 에 공시된 회사 리스트 불러오기
    corp_list = dart.get_corp_list()

    # 삼성전자 검색
    samsung = corp_list.find_by_corp_name('삼성전자', exactly=True)[0]

    # 2012년부터 연간 연결재무제표 불러오기
    fs = samsung.extract_fs(bgn_de='20120101')

    # 재무제표 검색 결과를 엑셀파일로 저장 ( 기본저장위치: 실행폴더/fsdata )
    fs.save()

주의사항
-------------

-   Open DART API는 일일 이용한도가 있으며, DART 홈페이지는 짧은 시간에 요청이 몰리면 IP 접속이 일정 시간 차단될 수 있음
-   `관련 공지사항 <https://opendart.fss.or.kr/cop/bbs/selectArticleList.do?bbsId=B0000000000000000002>`_
-   기본 요청 간격은 0.2초이며, 대량으로 조회할 경우 ``dart.utils.request.set_delay(1.0)`` 과 같이 간격을 늘리는 것을 권장


License
-------------
This project is licensed under the MIT License

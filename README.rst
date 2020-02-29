DART-FSS
===========================

..  image:: https://img.shields.io/pypi/v/dart-fss.svg
..  image:: https://img.shields.io/pypi/pyversions/dart-fss.svg
..  image:: https://travis-ci.com/josw123/dart-fss.svg?branch=master
..  image:: https://codecov.io/gh/josw123/dart-fss/branch/master/graphs/badge.svg
..  image:: https://api.codacy.com/project/badge/Grade/7ebb506ba99d4a22b2bbcda2d85b3bde

대한민국 금융감독원에서 운영하는 다트(`DART <https://dart.fss.or.kr>`_) 사이트 크롤링 및 재무제표 추출을 위한 라이브러리

Installation
---------------------------

..  code::

    pip install dart-fss

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

-   Open DART 및 DART 홈페이지의 경우 분당 100회 이상 요청시 서비스가 제한될 수 있음
-   `관련 공지사항 <https://bit.ly/2wcnz2y>`_


License
-------------
This project is licensed under the MIT License

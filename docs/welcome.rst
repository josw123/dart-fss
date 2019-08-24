DART-FSS
==========

..  image:: https://img.shields.io/pypi/v/dart-fss.svg
..  image:: https://img.shields.io/pypi/pyversions/dart-fss.svg
..  image:: https://travis-ci.com/josw123/dart-fss.svg?branch=master
..  image:: https://codecov.io/gh/josw123/dart-fss/branch/master/graphs/badge.svg
..  image:: https://api.codacy.com/project/badge/Grade/7ebb506ba99d4a22b2bbcda2d85b3bde

대한민국 금융감독원에서 운영하는 다트(`DART <https://dart.fss.or.kr>`_) 사이트 크롤링 및 재무제표 추출을 위한 라이브러리

Installation
------------

..  code::

    pip install dart-fss

DART API 신청
-------------
-   `DART API 신청 <https://dart.fss.or.kr/dsag002/insertForm.do>`_
-   `API Key 확인 <http://dart.fss.or.kr/dsap001/apikeyManagement.do>`_

Quick Starts
-------------
..  code:: python

    import dart_fss as dart

    # DART API KEY 설정
    api_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
    dart.dart_set_api_key(api_key=api_key)

    # 상장된 회사 리스트 불러오기
    crp_list = dart.get_crp_list()

    # 삼성전자 선택
    samsung = crp_list.find_by_name('삼성전자')[0]

    # 2012년부터 연간 연결재무제표 불러오기
    fs = samsung.get_financial_statement(start_dt='20120101')

    # 재무제표 검색 결과를 엑셀파일로 저장 ( 기본저장위치: 실행폴더/fsdata )
    fs.save()

주의사항
-------------

-   Dart-Fss 라이브러리는 오픈 API의 응답 방식 중 JSON 방식을 사용 중
-   현재 DART 오픈 API의 응답 방식이 JSON인 경우 오류 발생시 오류 메시지를 보내지 않음 (응답방식이 xml인 경우 올바르게 작동함)

[XML](http://dart.fss.or.kr/api/search.xml?auth=x&bsn_tp=a) 결과

..  code-block::

    <?xml version="1.0" encoding="utf-8"?>
    <result>
        <err_code>010</err_code>
        <err_msg>미등록 인증키</err_msg>
        <page_no>1</page_no>
        <page_set>10</page_set>
        <total_count>0</total_count>
        <total_page>0</total_page>
    </result>


[JSON](http://dart.fss.or.kr/api/search.json?auth=x&bsn_tp=a) 결과

.. code-block::

    {"err_code":"000","err_msg":"정상","page_no":1,"page_set":10,"total_count":0,"total_page":0,"list":[]}



DART 공시정보 검색
==================================

DART 공시 정보 검색
----------------------------------
DART에서 제공하는 OPEN API를 이용하여 공시 정보를 검색하는 함수

search_report
'''''''''''''''''''
..  autofunction:: dart_fss.search.search_report


search_report_with_cache
'''''''''''''''''''''''''''''

..  autofunction:: dart_fss.search.search_report_with_cache

..  note:: 기본 캐싱 시간: 30분

..  note:: 기본 캐싱 검색 결과 수 4개

Example
'''''''''''''

..  code-block:: python

    import dart_fss as dart

    # 2019년 1월 1일부터 2019년 3월 31일까지 검색 (crp_cd 미지정시 최대 3개월만 검색가능)
    reports = search_report(start_dt='20190101', end_dt='20190331')

    # 2019년 1월 1일부터 2019년 3월 31일까지 검색 (페이지당 표시 건수: 100)
    reports = search_report(start_dt='20190101', end_dt='20190331', page_set=100)

    # 2019년 5월 1일부터 2019년 7월 1일까지 연간보고서만 검색
    reports = search_report(start_dt='20190501', end_dt='20190701', bsn_tp='a001')

    # 2019년 5월 1일부터 2019년 7월 1일까지 연간보고서 및 반기보고서 검색
    reports = search_report(start_dt='20190501', end_dt='20190701', bsn_tp=['a001', 'a002'])



    # 최대 캐싱 시간 50분으로 변경
    dart.search.MAX_CACHED_MINUTES = 50

    # 최대 캐싱 검색 결과 6개로 변경
    MAX_CACHED_SEARCH_RESULTS = 6

    # 2019년 1월 1일부터 2019년 3월 31일까지 검색 ( 캐쉬 기능 사용 )
    reports = dart.search.search_report_with_cache(start_dt='20190101', end_dt='20190331')


SearchResults
----------------------------------

.. autoclass:: dart_fss.search.SearchResults
    :members:

Example
'''''''''''''

..  code-block:: python

    import dart_fss as dart

    '''
    # 삼성전자 선택
    samsung = crp_list.find_by_name('삼성전자')[0]
    # 연간보고서 검색
    reports = samsung.search_report(start_dt='20100101', bsn_tp='a001')

    위의 검색식과 아래 검색은 동일
    '''
    reports = search_report(crp_cd='005930', start_dt='20100101', bsn_tp='a001')

    # Reports의 Index는 0부터 시작
    # 가장 최신 보고서 선택
    newest_report = reports[0]

    # 0-4번 보고서 선택
    zero_to_fourth_report = reports[0:5]

    # 짝수번째 보고서 선택
    even_report = reports[::2]

    # 가장 오래된 보고서 선택
    oldest_report = reports[-1]

    # 최종보고서만 필터링
    filtered = reports.filter(fin_rpt=True)

    # 페이지당 표시할 리포트 수 변경
    reports.page_set = 100



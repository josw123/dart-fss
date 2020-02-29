DART 공시정보 검색
==================================

DART 공시 정보 검색
----------------------------------
Open DART에서 제공하는 OPEN API를 이용하여 공시 정보를 검색하는 함수

search_report
'''''''''''''''''''
..  autofunction:: dart_fss.filings.search

..  note:: :doc:`공시유형 및 공시상세유형 참고 <dart_types>`

Example
'''''''''''''

..  code-block:: python

    import dart_fss as dart

    # 2019년 1월 1일부터 2019년 3월 31일까지 검색 (crp_cd 미지정시 최대 3개월만 검색가능)
    reports = dart.filings.search(bgn_de='20190101', end_de='20190331')

    # 2019년 1월 1일부터 2019년 3월 31일까지 검색 (페이지당 표시 건수: 100)
    reports = dart.filings.search(bgn_de='20190101', end_de='20190331', page_count=100)

    # 2019년 5월 1일부터 2019년 7월 1일까지 연간보고서만 검색
    reports = dart.filings.search(bgn_de='20190501', end_de='20190701', pblntf_detail_ty='a001')

    # 2019년 5월 1일부터 2019년 7월 1일까지 연간보고서 및 반기보고서 검색
    reports = dart.filings.search(bgn_de='20190501', end_de='20190701', pblntf_detail_ty=['a001', 'a002'])

SearchResults
----------------------------------

.. autoclass:: dart_fss.filings.search.SearchResults
    :members:

Example
'''''''''''''

..  code-block:: python

    import dart_fss as dart

    # 삼성전자 code
    corp_code = '00126380'

    # 모든 상장된 기업 리스트 불러오기
    crp_list = get_corp_list()

    # 삼성전자
    samsung = corp_list.find_by_corp_name(corp_code=corp_code)

    # 연간보고서 검색
    # reports = samsung.search_filings(bgn_de='20100101', pblntf_detail_ty='a001')
    reports = search_report(corp_code=corp_code, bgn_de='20100101', pblntf_detail_ty='a001')

    # Reports의 Index는 0부터 시작
    # 가장 최신 보고서 선택
    newest_report = reports[0]

    # 0-4번 보고서 선택
    zero_to_fourth_report = reports[0:5]

    # 짝수번째 보고서 선택
    even_report = reports[::2]

    # 가장 오래된 보고서 선택
    oldest_report = reports[-1]


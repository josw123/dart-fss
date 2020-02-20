기업정보검색
==================================

상장된 기업 정보 불러오기
----------------------------------
DART에 공시된 회사리스트를 반환하는 클래스.

.. autoclass:: dart_fss.CorpList
    :members:

Example
'''''''''''''

..  code-block:: python

    from dart_fss import CorpList

    # 모든 상장된 기업 리스트 불러오기
    crp_list = CorpList()

    # 삼성전자를 이름으로 찾기 ( 리스트 반환 )
    samsung = corp_list.find_by_name('삼성전자', exactly=True)[0]

    # "삼성"을 포함한 모든 공시 대상 찾기
    corps = corp_list.find_by_name('삼성')

    # 증권 코드를 이용한 찾기
    samsung = corp_list.find_by_stock_code('005930')

    # 다트에서 사용하는 회사코드를 이용한 찾기
    samsung = corp_list.find_by_corp_code('00126380')

기업정보(Crp)
----------------------------------

.. autoclass:: dart_fss.corp.Corp
    :members:

Example
'''''''''''''

..  code-block:: python

    # 2019년 3월 1일부터 2019년 5월 31일까지 삼성전자의 모든 공시 정보 조회
    reports = samsung.search_filings(bgn_de='20190301', end_de='20190531')

    # 2010년 1월 1일부터 현재까지 모든 사업보고서 검색
    reports = samsung.search_filings(bgn_de='20100101', pblntf_detail_ty='a001')

    # 2010년 1월 1일부터 현재까지 모든 사업보고서의 최종보고서만 검색
    reports = samsung.search_filings(bgn_de='20100101', pblntf_detail_ty='a001', last_reprt_at='Y')

    # 2010년 1월 1일부터 현재까지 사업보고서, 반기보고서, 분기보고서 검색
    reports = samsung.search_filings(bgn_de='20100101', pblntf_detail_ty=['a001', 'a002', 'a003'])

    # 2012년 1월 1일부터 현재까지 연간 연결재무제표 검색
    fs = samsung.extract_fs(bgn_de='20120101')

    # 2012년 1월 1일부터 현재까지 분기 연결재무제표 검색 (연간보고서, 반기보고서 포함)
    fs_quarter = samsung.extract_fs(bgn_de='20120101', report_tp='quarter')

    # 2012년 1월 1일부터 현재까지 개별재무제표 검색
    fs_separate = samsung.extract_fs(bgn_de='20120101', separate=True)


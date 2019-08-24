기업정보검색
==================================

상장된 기업 정보 불러오기
----------------------------------
유가증권시장, 코스닥시장, 코넥스시에 상장된 회사리스트를 불러오는 함수로 CrpList를 반환한다.

..  autofunction:: dart_fss.crp.get_crp_list

Example
'''''''''''''

..  code-block:: python

    import dart_fss as dart

    # 모든 상장된 기업 리스트 불러오기
    crp_list = dart.get_crp_list()

    # 코스피 시장에 상장된 기업 리스트 불러오기
    stock_list = dart.get_crp_list(market='Y')

    # 코스닥 시장에 상장된 기업 리스트 불러오기
    kosdaq_list = dart.get_crp_list(market='K')

    # 코스넥 시장에 상장된 기업 리스트 불러오기
    konex_list = dart.get_crp_list(market='N')


CrpList
------------------------

get_crp_list의 검색결과로 이름, 코드, 취급 물품등으로 회사를 검색할 수 있다.

.. autoclass:: dart_fss.crp.CrpList

Example
'''''''''''''

..  code-block:: python

    # 삼성전자 찾기 / 검색된 리스트 반환
    samsung = crp_list.find_by_name('삼성전자')[0]

    # 삼성전자를 회사코드로 찾기 / Crp Object 반환
    samsung = crp_list.find_by_crp_cd('005930')

    # 취급 물품으로 찾기 /
    medical_crp_list = crp_list.find_by_product('의료기기')

기업정보(Crp)
----------------------------------

.. autoclass:: dart_fss.crp.Crp
    :members:

Example
'''''''''''''

..  code-block:: python

    # 2019년 3월 1일부터 2019년 5월 31일까지 삼성전자의 모든 공시 정보 조회
    reports = samsung.search_report(star_td='20190301', end_dt='20190531')

    # 2010년 1월 1일부터 현재까지 모든 사업보고서 검색
    reports = samsung.search_report(start_dt='20100101', bsn_tp='a001')

    # 2010년 1월 1일부터 현재까지 모든 사업보고서의 최종보고서만 검색
    reports = samsung.search_report(start_dt='20100101', bsn_tp='a001', fin_rpt=True)

    # 2010년 1월 1일부터 현재까지 사업보고서, 반기보고서, 분기보고서 검색
    reports = samsung.search_report(start_dt='20100101', bsn_tp=['a001', 'a002', 'a003'])

    # 2012년 1월 1일부터 현재까지 연간 연결재무제표 검색
    fs = samsung.get_financial_statement(start_dt='20120101')

    # 2012년 1월 1일부터 현재까지 분기 연결재무제표 검색 (연간보고서, 반기보고서 포함)
    fs_quarter = samsung.get_financial_statement(start_dt='20120101', report_tp='quarter')

    # 2012년 1월 1일부터 현재까지 개별재무제표 검색
    fs_separate = samsung.get_financial_statement(start_dt='20120101', separate=True)


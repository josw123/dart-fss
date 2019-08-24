XBRL 데이터 추출
======================================

DartXbrl 클래스
----------------------------------

.. autoclass:: dart_fss.xbrl.DartXbrl
    :members:

Table 클래스
----------------------------------

.. autoclass:: dart_fss.xbrl.Table
    :members:

Example
----------------------------------

.. code-block:: python

    import dart_fss as dart

    crp_list = dart.get_crp_list()
    samsung = crp_list.find_by_name('삼성전자')[0]

    reports = samsung.search_reports(start_dt='20190101', bsn_tp='a001')
    report = reports[0]

    # 리포트의 xbrl 데이터
    xbrl = report.xbrl

    # 연결재무제표 존재 여부 확인
    xbrl.exist_consolidated()

    # 감사 정보 (영문) -> DataFrame 형태로 반환됨
    audit = xbrl.get_audit_information(lang='en')

    # 연결 현금흐름표 추출 (리스트 반환)
    cf = xbrl.get_cash_flows()
    # 삼성전자의 경우 존재하므로 /
    cf = cf[0]

    # Pandas DataFrame으로 변환
    df = cf.to_DataFrame()

    # Pandas DataFrame으로 변환 / 분류 정보 제외
    df_wo_class = cf.to_DataFrame(show_class=False)
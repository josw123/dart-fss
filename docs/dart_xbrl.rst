XBRL 데이터 추출
======================================

XBRL 파일 데이터 분석
----------------------------------

.. autofunction:: dart_fss.xbrl.get_xbrl_from_file


DartXbrl 클래스
----------------------------------

.. autoclass:: dart_fss.xbrl.dart_xbrl.DartXbrl
    :members:

Table 클래스
----------------------------------

.. autoclass:: dart_fss.xbrl.table.Table
    :members:

Example
----------------------------------

.. code-block:: python

    import dart_fss as dart


    # 삼성전자 code
    corp_code = '00126380'

    # 모든 상장된 기업 리스트 불러오기
    crp_list = get_corp_list()

    # 삼성전자
    samsung = corp_list.find_by_corp_name(corp_code=corp_code)

    # 사업보고서 검색
    reports = samsung.search_filings(start_dt='20190101', pblntf_detail_ty='a001')

    # 첫번째 리포트 선택
    report = reports[0]

    # 리포트의 xbrl 데이터
    xbrl = report.xbrl

    # 연결재무제표 존재 여부 확인( True / False)
    xbrl.exist_consolidated()

    # 감사 정보 (영문) -> DataFrame 형태로 반환됨
    audit = xbrl.get_audit_information(lang='en')

    # 연결 현금흐름표 추출 (리스트 반환)
    cf = xbrl.get_cash_flows()

    # 연결 현금프름표
    cf = cf[0]

    # Pandas DataFrame으로 변환
    df = cf.to_DataFrame()

    # Pandas DataFrame으로 변환 / 분류 정보 제외
    df_wo_class = cf.to_DataFrame(show_class=False)
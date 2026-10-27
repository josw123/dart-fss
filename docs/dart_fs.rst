재무제표 일괄 추출
=================================

재무제표 추출
'''''''''''''

..  autofunction:: dart_fss.fs.extract

FinancialStatement 클래스
''''''''''''''''''''''''''''''''''''

재무제표 일괄 추출의 결과를 담고 있는 클래스

.. autoclass:: dart_fss.fs.FinancialStatement
    :members:

Example
'''''''''''''

..  code-block:: python

    import dart_fss as dart

    # 삼성전자 code
    corp_code = '00126380'

    # 모든 상장된 기업 리스트 불러오기
    corp_list = dart.get_corp_list()

    # 삼성전자
    samsung = corp_list.find_by_corp_code(corp_code=corp_code)

    # 2012년 01월 01일 부터 연결재무제표 검색
    # fs = samsung.extract_fs(bgn_de='20120101') 와 동일
    fs = dart.fs.extract(corp_code=corp_code, bgn_de='20120101')

    # 여러 보고서를 추출할 때 XBRL 분석을 병렬로 수행 (결과 동일, 다운로드는 순차)
    # 스크립트로 실행할 경우 if __name__ == '__main__': 블록 안에서 호출
    # fs = dart.fs.extract(corp_code=corp_code, bgn_de='20120101', workers=4)

    # 연결재무상태표
    df_fs = fs['bs'] # 또는 fs[0], 표시 옵션 적용: fs.show('bs', show_depth=1)
    # 연결재무상태표 추출에 사용된 Label 정보
    labels_fs = fs.labels['bs']

    # 연결손익계산서
    df_is = fs['is'] # 또는 fs[1]
    # 연결손익계산서 추출에 사용된 Label 정보
    labels_is = fs.labels['is']

    # 연결포괄손익계산서
    df_ci = fs['cis'] # 또는 fs[2]
    # 연결포괄손익계산서 추출에 사용된 Label 정보
    labels_ci = fs.labels['cis']

    # 현금흐름표
    df_cf = fs['cf'] # 또는 fs[3]
    # 현금흐름표 추출에 사용된 Label 정보
    labels_cf = fs.labels['cf']

    # 재무제표 일괄저장 (default: 실행폴더/fsdata/{corp_code}_{report_tp}.xlsx)
    fs.save()

    # 재무제표 일괄저장
    filename = '삼성전자.xlsx'
    path = '/User/xxxxx/Desktop/'
    fs.save(filename=filename, path=path)

    # 저장한 재무제표 불러오기
    fs = dart.fs.FinancialStatement.load('/User/xxxxx/Desktop/삼성전자.xlsx')

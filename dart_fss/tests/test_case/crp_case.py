from .testcrp import TestCrp

# 삼성전자 테스트
samsung = TestCrp(crp_cd='005930', start_dt='20110101', separate=False, report_tp='annual')
samsung.add_test_value('fs', '20091231', 'concept_id', 'ifrs_Equity', 73045202000000)
samsung.add_test_value('is', '20091231', 'label_ko', '영업이익(손실)', 10925259000000)
samsung.add_test_value('ci', '20091231', 'label_ko', '총포괄손익', 9098844000000)
samsung.add_test_value('cf', '20091231', 'label_ko', '기말현금및현금성자산', 10149930000000)

# 현대자동차 테스트
hyundai = TestCrp(crp_nm='현대자동차', start_dt='20120101', separate=False, report_tp='annual')
hyundai.add_test_value('fs', '20101231', 'label_ko', '유동자산', 43520154000000)
hyundai.add_test_value('is', '20101231', 'label_ko', '영업이익', 5918492000000)
hyundai.add_test_value('ci', '20101231', 'concept_id', 'ifrs_ComprehensiveIncome', 6223342000000)
hyundai.add_test_value('cf', '20101231', 'concept_id', 'dart_CashAndCashEquivalentsAtEndOfPeriodCf', 6215815000000)

# 덱스터 테스트
dexter = TestCrp(crp_cd='206560', start_dt='20120101', separate=False, report_tp='annual')
dexter.add_test_value('fs', '20141231', 'concept_id', 'ifrs_CurrentAssets', 14049343213)
dexter.add_test_value('fs', '20161231', 'concept_id', 'ifrs_Equity', 78181834231)

stone = TestCrp(crp_nm='두원석재', start_dt='20120101', separate=True, report_tp='annual')
stone.add_test_value('fs', '20161231', 'label_ko', 'Ⅰ.유동자산', 5531436227)

test_crp_list = [samsung, hyundai, dexter, stone]

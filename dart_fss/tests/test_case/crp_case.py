from .testcrp import TestCrp

# 삼성전자
samsung = TestCrp(corp_code='00126380', bgn_de='20110101', separate=False, report_tp='annual')
samsung.add_test_value('bs', '20091231', 'concept_id', 'ifrs_Equity', 73045202000000)
samsung.add_test_value('is', '20091231', 'label_ko', '영업이익(손실)', 10925259000000)
samsung.add_test_value('cis', '20091231', 'label_ko', '총포괄손익', 9098844000000)
samsung.add_test_value('cf', '20091231', 'label_ko', '기말현금및현금성자산', 10149930000000)

# 현대자동차
hyundai = TestCrp(corp_code='00164742', bgn_de='20120101', separate=False, report_tp='annual')
hyundai.add_test_value('bs', '20101231', 'label_ko', '유동자산', 43520154000000)
hyundai.add_test_value('is', '20101231', 'label_ko', '영업이익', 5918492000000)
hyundai.add_test_value('cis', '20101231', 'concept_id', 'ifrs_ComprehensiveIncome', 6223342000000)
hyundai.add_test_value('cf', '20101231', 'concept_id', 'dart_CashAndCashEquivalentsAtEndOfPeriodCf', 6215815000000)

# 덱스터
dexter = TestCrp(corp_code='01021949', bgn_de='20120101', separate=False, report_tp='annual')
dexter.add_test_value('bs', '20141231', 'concept_id', 'ifrs_CurrentAssets', 14049343213)
dexter.add_test_value('bs', '20161231', 'concept_id', 'ifrs_Equity', 78181834231)

# 이십일스토어 (구: 두원석재)
stone = TestCrp(corp_code='01183407', bgn_de='20120101', separate=True, report_tp='annual')
stone.add_test_value('bs', '20161231', 'label_ko', 'Ⅰ.유동자산', 5531436227)

test_crp_list = [samsung, hyundai, dexter, stone]

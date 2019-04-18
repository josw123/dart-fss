from .testcrp import TestCrp

# 삼성전자 테스트
samsung_fs = TestCrp(crp_cd='005930')
samsung_fs.add_test_set('fs', '20120101', 'concept_id', '20091231', 'ifrs_Equity', 73045202000000)
samsung_is = TestCrp(crp_cd='005930')
samsung_is.add_test_set('is', '20120101', 'label_ko', '20091231', '영업이익(손실)', 10925259000000)
samsung_ci = TestCrp(crp_cd='005930')
samsung_ci.add_test_set('ci', '20120101', 'label_ko', '20091231', '총포괄손익', 9098844000000)
samsung_cf = TestCrp(crp_cd='005930')
samsung_cf.add_test_set('cf', '20120101', 'label_ko', '20091231', '기말현금및현금성자산', 10149930000000)

# 현대자동차 테스트
hyundai_fs = TestCrp(crp_nm='현대자동차')
hyundai_fs.add_test_set('fs', '20120101', 'label_ko', '20101231', '유동자산', 43520154000000)
hyundai_is = TestCrp(crp_nm='현대자동차')
hyundai_is.add_test_set('is', '20120101', 'label_ko', '20101231', '영업이익', 5885960000000)
hyundai_ci = TestCrp(crp_nm='현대자동차')
hyundai_ci.add_test_set('ci', '20120101', 'concept_id', '20101231',
                        'ifrs_ComprehensiveIncome', 6223342000000)
hyundai_cf = TestCrp(crp_nm='현대자동차')
hyundai_cf.add_test_set('cf', '20120101', 'concept_id', '20101231',
                        'dart_CashAndCashEquivalentsAtEndOfPeriodCf', 6215815000000)

test_crp_list = [samsung_fs, samsung_is, samsung_ci, samsung_cf, hyundai_fs, hyundai_is, hyundai_ci, hyundai_cf]

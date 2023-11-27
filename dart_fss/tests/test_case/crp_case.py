from .testcrp import TestCrp

# 삼성전자
samsung = TestCrp(corp_code='00126380', bgn_de='20110101',
                  separate=False, report_tp='annual')
samsung.add_test_value('bs', '20091231', 'concept_id',
                       'ifrs-full_Equity', 73045202000000)
samsung.add_test_value('is', '20091231', 'concept_id',
                       'dart_OperatingIncomeLoss', 10925259000000)
samsung.add_test_value('cis', '20091231', 'label_ko', '총포괄손익', 9098844000000)
samsung.add_test_value('cf', '20091231', 'concept_id',
                       'dart_CashAndCashEquivalentsAtEndOfPeriodCf', 10149930000000)
samsung.add_test_value('cf', '20151231', 'concept_id',
                       'ifrs-full_InterestPaidClassifiedAsOperatingActivities', 748256000000)
samsung.add_test_value('is', '20151231', 'concept_id', 'ifrs-full_BasicEarningsLossPerShare', 126305)

# XBRL Viewer 업데이트로 인한 테스트 케이스(#146)
samsung2 = TestCrp(corp_code='00126380', bgn_de='20220101', end_de='20231231',
                   separate=False, report_tp='quarter')
samsung2.add_test_value('bs', '20220930', 'concept_id','ifrs-full_CurrentAssets', 250880637000000)

# 현대자동차
hyundai = TestCrp(corp_code='00164742', bgn_de='20120101',
                  separate=False, report_tp='annual')
hyundai.add_test_value('bs', '20101231', 'label_ko', '유동자산', 43520154000000)
hyundai.add_test_value('is', '20101231', 'label_ko', '영업이익', 5885960000000)
hyundai.add_test_value('cis', '20101231', 'concept_id',
                       'ifrs-full_ComprehensiveIncome', 6223342000000)
hyundai.add_test_value('cf', '20101231', 'concept_id',
                       'dart_CashAndCashEquivalentsAtEndOfPeriodCf', 6215815000000)

# 덱스터
dexter = TestCrp(corp_code='01021949', bgn_de='20120101',
                 separate=False, report_tp='annual')
dexter.add_test_value('bs', '20141231', 'concept_id',
                      'ifrs-full_CurrentAssets', 14049343213)
dexter.add_test_value('bs', '20161231', 'concept_id',
                      'ifrs-full_Equity', 78181834231)

# 이십일스토어 (구: 두원석재)
stone = TestCrp(corp_code='01183407', bgn_de='20120101',
                separate=True, report_tp='annual')
stone.add_test_value('bs', '20161231', 'label_ko', 'I.유동자산', 5531436227)

# 에스제이그룹
sjgroup = TestCrp(corp_code='01222432', bgn_de='20190101',
                  separate=False, report_tp='annual')
sjgroup.add_test_value('bs', '20191231', 'label_ko', '유동자산', 70665507683)

# 삼성에스디에스 분기 검색
sds = TestCrp(corp_code='00126186', bgn_de='20130813',
              end_de='20150807', separate=False, report_tp='quarter')
sds.add_test_value('bs', '20130630', 'label_ko', '유동자산', 2602291807082)

# JTC
jtc = TestCrp(corp_code='01041828', bgn_de='20190101',
              end_de='20200811', separate=False, report_tp='annual')
jtc.add_test_value('cf', '20200229', 'concept_id',
                   'ifrs-full_CashFlowsFromUsedInOperatingActivities', 4810599061)

# GS리테일
gs_retail = TestCrp(corp_code='00140177', bgn_de='20110101',
                    separate=False, report_tp='annual')
gs_retail.add_test_value('cis', '20161231', 'label_ko', '매출원가', 6015117323057)
gs_retail.add_test_value('cis', '20161231', 'label_ko', '기타손실', 60931373946)
gs_retail.add_test_value('cis', '20161231', 'label_ko',
                         '판매비와관리비', 1168120874437)
gs_retail.add_test_value('cis', '20161231', 'label_ko', '금융원가', 48502482146)

# LG화학
lg_chemical = TestCrp(corp_code='00356361', bgn_de='20180101',
                      end_de='20201231', separate=False, report_tp='quarter')
lg_chemical.add_test_value('cis', '20180701-20180930',
                           'concept_id', 'ifrs-full_ProfitLoss', 346600000000)

# LG화학
lg_chemical2 = TestCrp(corp_code='00356361', bgn_de='20120101',
                       end_de='20201231', separate=False, report_tp='annual')
lg_chemical2.add_test_value(
    'is', '20120101-20121231', 'label_ko', '보통주기본주당이익', 20318)

# 메리츠 화재 (#55)
meritz_fire = TestCrp(corp_code='00117744', bgn_de='20140101',
                      end_de='20141231', separate=False, report_tp='annual')
meritz_fire.add_test_value('cis', '20130401-20131231',
                           'label_ko', 'Ⅷ.연결당기순이익', 135682814119)

# 하나 금융 투자 (#54)
hana_fn = TestCrp(corp_code='00547583', bgn_de='20120101',

                  end_de='20121231', separate=False, report_tp='annual')
hana_fn.add_test_value('bs', '20100101', 'label_ko', '부채총계', 139823866000000)

# 아세아 제지 (#63)
asia_paper = TestCrp(corp_code='00138729', bgn_de='20180101', end_de='20200331', separate=False, report_tp='annual')
asia_paper.add_test_value('bs', '20181231', 'label_ko', '유동자산', 280262148456)

# 부국증권 (#66)
bookook = TestCrp(corp_code='00123772', bgn_de='20200101', end_de='20210503', separate=False, report_tp='annual')
bookook.add_test_value('bs', '20201231', 'label_ko', '부채및자본총계', 1608864797228)

# 바이온 (# 79)
byon = TestCrp(corp_code='00232089', bgn_de='20100101', end_de='20100701', separate=True, report_tp=['quarter'])
byon.add_test_value('bs', '20100331', 'label_ko', '유동자산', 2722479385)


test_crp_list = [samsung, samsung2, hyundai, dexter, stone, sjgroup, sds,
                 jtc, gs_retail, lg_chemical, lg_chemical2, meritz_fire, hana_fn, asia_paper, bookook, byon]

# Dart-Fss
![PyPI](https://img.shields.io/pypi/v/dart-fss.svg)
[![Build Status](https://travis-ci.com/josw123/dart-fss.svg?branch=master)](https://travis-ci.com/josw123/dart-fss)
[![Coverage](https://codecov.io/gh/josw123/dart-fss/branch/master/graphs/badge.svg)](https://codecov.io/gh/josw123/dart-fss)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7ebb506ba99d4a22b2bbcda2d85b3bde)](https://www.codacy.com/app/josw123/dart-fss?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=josw123/dart-fss&amp;utm_campaign=Badge_Grade)

한국 금융감독원에서 운영하는 Dart 시스템 크롤링을 위한 라이브러리

## Features

-   [KIND](http://kind.krx.co.kr)를 이용한 기업정보 검색
-   [DART](http://dart.fss.or.kr)의 오픈 API를 이용한 전자공시 조회
-   [DART](http://dart.fss.or.kr)의 전자공시 정보를 이용한 재무제표 추출

## Installation
```bash
pip install dart-fss
```

## Dependencies

-   [NumPy](https://www.numpy.org/)
-   [pandas](https://pandas.pydata.org/)
-   [requests](http://docs.python-requests.org/en/master/)
-   [lxml](https://github.com/lxml/lxml)
-   [beautifulsoup4](https://www.crummy.com/software/BeautifulSoup/)
-   [arelle](http://arelle.org/)
-   [isodate](https://github.com/gweis/isodate/)
-   [tqdm](https://github.com/tqdm/tqdm)
-   [fake-useragent](https://github.com/hellysmile/fake-useragent)

## Usage

### Dart API Key 설정

환경 변수 DART_API_KEY 설정

또는 패키지 사용전 아래와 같이 설정

```python
import dart_fss as dart

api_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' 
dart.dart_set_api_key(api_key=api_key)
```

### 상장된 회사리스트
```python
import dart_fss as dart

# Market Type
# A: 모든 시장
# Y: 유가증권시장
# K: 코스닥
# N: 코넥스
# E: 기타

crp_list = dart.get_crp_list() # default 모든 시장
crp_list_stock = dart.get_crp_list(market='y') # 유가증권시장

# 이름으로 검색
samsung_electronics = crp_list.find_by_name('삼성전자')[0] # 리스트 반환

# 코드로 검색
sk_hynix = crp_list_stock.find_by_crp_cd('000660') # 특정 종목 반환

# 관련 물품으로 검색
stock_brokers = crp_list.find_by_product('증권') # 리스트 반환
```

### Dart 전자공시 조회

```python
import dart_fss as dart

crp_list = dart.get_crp_list() # default 모든 시장
samsung_electronics = crp_list.find_by_name('삼성전자')[0] # 리스트 반환

# 오늘 공시된 전자공시 조회
today = dart.search_report() 

# 특정기간 검색 (3개월 이내)
reports = dart.search_report(start_dt='20190101',end_dt='20190201')
reports.page_no = 2     # 2번째 페이지로 이동
reports.next_page()     # 다음 페이지로 이동
reports.prev_page()     # 이전 페이지로 이동

# 특정회사 검색 
reports = dart.search_report(crp_cd='000660', start_dt='20190101') # 하이닉스
# 또는
reports = samsung_electronics.search_report(start_dt='20190101')

# 검색결과 필터링
reports = reports.filter(bsn_tp='a001') # 연말보고서만 출력

annual_report = reports[0] # 2019년 사업보고서
annual_report.pages # 2019년 사업보고서 Page List 출력

# 3번째 페이지 조회
page = annual_report[3]

# 3번째 페이지의 HTML 
html = page.html

annual_report.to_file(r'C:\annual_report_2019') # C:\annual_report_2019에 사업보고서 저장(html 파일 형태로 파일별로 저장)

# "연결재무제표" 포함, "주석" 미포함 페이지만 로딩
annual_report.load_page(includes="연결재무제표", excludes="주석")
```

### 제무제표 검색

제무제표는 pandas의 DataFrame 형태로 반환 된다.
또한 각각의 회사마다 동일한 항목에 대하여 다른 명칭을 사용하는 경우가 있기 때문에 concept을 이용하여 구분하는 것이 편하다.

```python
import dart_fss as dart

crp_list = dart.get_crp_list() # 유가증권시장
samsung_electronics = crp_list.find_by_name('삼성전자')[0]

# 2012년부터 연간보고서에 포함된 연결 재무상태표 검색
fs_annual = samsung_electronics.get_financial_statement(start_dt='20120101')

# 2012년부터 연간보고서에 포함된 연결 재무상태표 검색(반기 포함)
fs_half = samsung_electronics.get_financial_statement(start_dt='20120101', report_tp='half')

# 2012년부터 연간보고서에 포함된 연결재무상태표 검색(반기 및 분기 포함)
fs_quarter = samsung_electronics.get_financial_statement(start_dt='20120101', report_tp='quarter')

# 2012년부터 연결 손익계산서 검색(회사에 따라 제공되지 않는경우도 있음)
fs_annual = samsung_electronics.get_financial_statement(start_dt='20120101', fs_tp='is')

# 2012년부터 연결 포괄손익계산서 검색(회사에 따라 제공되지 않는경우도 있음)
ci_annual = samsung_electronics.get_financial_statement(start_dt='20120101', fs_tp='ci')

# 2012년부터 연결 현금흐름표 검색
cf_annual = samsung_electronics.get_financial_statement(start_dt='20120101', fs_tp='cf')

# 표시언어 영어(기본 'ko')
fs_annual = samsung_electronics.get_financial_statement(start_dt='20120101', lang='en')

# Abstract 표시(기본 False)
fs_annual = samsung_electronics.get_financial_statement(start_dt='20120101', show_abstract=True)

# Class 표시 안함(기본 True)
fs_annual = samsung_electronics.get_financial_statement(start_dt='20120101', show_class=False)

# 표시할 Class 깊이(기본 10)
fs_annual = samsung_electronics.get_financial_statement(start_dt='20120101', show_depth=3)

# concept 표시 안함(기본 True)
fs_annual = samsung_electronics.get_financial_statement(start_dt='20120101', show_concept=False)

# 개별기업 연결 재무상태표 검색(기본 False)
fs_annual = samsung_electronics.get_financial_statement(start_dt='20120101', separate=True)

# 1000단위 구분자 표시여부(기본 True)
fs_annual = samsung_electronics.get_financial_statement(start_dt='20120101', separator=False)

```

### 주의사항

현재 DART 오픈 API의 응답방식이 JSON인 경우 오류 발생시 오류 메시지를 보내지 않음
(응답방식이 xml인 경우 올바르게 작동함)

http://dart.fss.or.kr/api/search.xml?auth=x&bsn_tp=a
```xml
<?xml version="1.0" encoding="utf-8"?>
<result>
    <err_code>010</err_code>
    <err_msg>미등록 인증키</err_msg>
    <page_no>1</page_no>
    <page_set>10</page_set>
    <total_count>0</total_count>
    <total_page>0</total_page>
</result>
```

http://dart.fss.or.kr/api/search.json?auth=x&bsn_tp=a
```json
{"err_code":"000","err_msg":"정상","page_no":1,"page_set":10,"total_count":0,"total_page":0,"list":[]}
```
# Dart-Fss
[![PyPI](https://img.shields.io/pypi/v/dart-fss.svg)](https://pypi.org/project/dart-fss/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dart-fss.svg)
[![Build Status](https://travis-ci.com/josw123/dart-fss.svg?branch=master)](https://travis-ci.com/josw123/dart-fss)
[![Coverage](https://codecov.io/gh/josw123/dart-fss/branch/master/graphs/badge.svg)](https://codecov.io/gh/josw123/dart-fss)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7ebb506ba99d4a22b2bbcda2d85b3bde)](https://www.codacy.com/app/josw123/dart-fss?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=josw123/dart-fss&amp;utm_campaign=Badge_Grade)

한국 금융감독원에서 운영하는 Dart 시스템 크롤링을 위한 라이브러리

- Documentation: https://dart-fss.readthedocs.io
- Source code: https://github.com/josw123/dart-fss

## Features

-   [KIND](http://kind.krx.co.kr)를 이용한 기업정보 검색
-   [DART](http://dart.fss.or.kr)의 오픈 API를 이용한 전자공시 조회
-   [DART](http://dart.fss.or.kr)의 전자공시 정보를 이용한 재무제표 추출

## Installation
```bash
pip install dart-fss
```

## Plugins
-   [Dart-Fss-Classifier](https://github.com/josw123/dart-fss-classifier): 재무제표 추출 성능 향상

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
-   [html5lib](https://github.com/html5lib/html5lib-python)
-   [openpyxl](https://openpyxl.readthedocs.io/en/stable/)
-   [halo](https://github.com/manrajgrover/halo)

## Usage

### Dart API Key 설정

-  [DART API 신청](https://dart.fss.or.kr/dsag002/insertForm.do)
-  [API Key 확인](http://dart.fss.or.kr/dsap001/apikeyManagement.do)
-  환경 변수 DART_API_KEY 설정 또는 패키지 사용전 아래와 같이 설정

```python
import dart_fss as dart

api_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx' 
dart.dart_set_api_key(api_key=api_key)
```

### 오류 코드 

- DartAPIError: DART API 에서 오류 메시지를 전송 받았을때 발생하는 오류
- NotFoundConsolidated: 연결재무제표가 없을때 발생하는 오류(해당사항이 없는 경우)

### 주의사항

-   Dart-Fss 라이브러리는 오픈 API의 응답 방식 중 JSON 방식을 사용 중
-   현재 DART 오픈 API의 응답 방식이 JSON인 경우 오류 발생시 오류 메시지를 보내지 않음 (응답방식이 xml인 경우 올바르게 작동함)

[XML](http://dart.fss.or.kr/api/search.xml?auth=x&bsn_tp=a) 결과
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

[JSON](http://dart.fss.or.kr/api/search.json?auth=x&bsn_tp=a) 결과
```json
{"err_code":"000","err_msg":"정상","page_no":1,"page_set":10,"total_count":0,"total_page":0,"list":[]}
```

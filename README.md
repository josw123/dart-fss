# DART-FSS (Data Analysis, Retrieval and Transfer System-Financial Supervisory Service)
[![PyPI](https://img.shields.io/pypi/v/dart-fss.svg)](https://pypi.org/project/dart-fss/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dart-fss.svg)
![Build Status](https://bit.ly/3fufevG)
[![Coverage](https://codecov.io/gh/josw123/dart-fss/branch/master/graphs/badge.svg)](https://codecov.io/gh/josw123/dart-fss)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7ebb506ba99d4a22b2bbcda2d85b3bde)](https://www.codacy.com/app/josw123/dart-fss?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=josw123/dart-fss&amp;utm_campaign=Badge_Grade)

대한민국 금융감독원에서 운영하는 다트([DART](https://dart.fss.or.kr)) 사이트 크롤링 및 재무제표 추출을 위한 라이브러리

A library for crawling and extracting financial statements of [DART](https://dart.fss.or.kr) operated by the FSS of Korea
- Source code: https://github.com/josw123/dart-fss

## Features
- [Open DART](https://opendart.fss.or.kr/)의 오픈 API를 이용한 전자공시 조회 (view DART with the open API)
- [DART](https://dart.fss.or.kr)의 전자공시 정보를 이용한 재무제표 추출 (extract financial statements using DART)
- [DART](https://dart.fss.or.kr)'s 

## Installation
- Open DART 지원 / 신규 Open DART API Key 필요
- Supports Open DART / Require new Open API Key
- Documentation: https://dart-fss.readthedocs.io/

``` bash
pip install dart-fss
```

## Plugins
- [Dart-Fss-Classifier](https://github.com/josw123/dart-fss-classifier): 재무제표 추출 성능 향상 (Improve performance of financial statements extraction)

## Usage

### DART API Key 설정 (Setting)
- [OPEN DART API Register](https://opendart.fss.or.kr/)
- 환경 변수 DART_API_KEY 설정 또는 패키지 사용전 아래와 같이 설정
- Setting the environment variable DART_API_KEY or before using the package as follows

### Quick Starts

```python
import dart_fss as dart

# Open DART API KEY 설정 (Setting)
api_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
dart.set_api_key(api_key=api_key)

# DART에 공시된 회사 리스트 불러오기
# Call a list of companies published in DART
corp_list = dart.get_corp_list()

# 삼성전자 검색
# Search for Samsung
samsung = corp_list.find_by_corp_name('삼성전자', exactly=True)[0]

# 2012년부터 연간 연결재무제표 불러오기
# Call annual consolidated financial statements from 2012
fs = samsung.extract_fs(bgn_de='20120101')

# 재무제표 검색 결과를 엑셀파일로 저장 ( 기본저장위치: 실행폴더/fsdata )
# Save the results of the financial statements search as an Excel file ( default storage location: execution folder/fsdata )
fs.save()
```

## 주의사항 (Precautions)
- Open DART 및 DART 홈페이지의 경우 분당 1000회 이상 요청시 서비스가 제한될 수 있음.
- For Open DART & DART homepage, service may be restricted if requested more than 1000 times per minute.
- [관련 공지사항](https://bit.ly/3cjF3Np): [FAQ] --> [오픈 API 이용한도는 어떻게 되나요?]
- [Related Notice](https://bit.ly/3cjF3Np): [FAQ] --> [What is the usage limit of the open API?]

## License
This project is licensed under the MIT License

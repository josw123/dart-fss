# Dart-Fss
[![PyPI](https://img.shields.io/pypi/v/dart-fss.svg)](https://pypi.org/project/dart-fss/)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dart-fss.svg)
![Build Status](https://bit.ly/313BAwe)
[![Coverage](https://codecov.io/gh/josw123/dart-fss/branch/master/graphs/badge.svg)](https://codecov.io/gh/josw123/dart-fss)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7ebb506ba99d4a22b2bbcda2d85b3bde)](https://www.codacy.com/app/josw123/dart-fss?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=josw123/dart-fss&amp;utm_campaign=Badge_Grade)

대한민국 금융감독원에서 운영하는 다트([DART](https://dart.fss.or.kr)) 사이트 크롤링 및 재무제표 추출을 위한 라이브러리

- Source code: https://github.com/josw123/dart-fss

## Features

-   [Open DART](https://opendart.fss.or.kr/)의 오픈 API를 이용한 전자공시 조회
-   [DART](http://dart.fss.or.kr)의 전자공시 정보를 이용한 재무제표 추출

## Installation

- Open DART 지원 / 신규 Open DART API Key 필요
- Documentation: https://dart-fss.readthedocs.io/

``` bash
pip install dart-fss
```

## Plugins
-   [Dart-Fss-Classifier](https://github.com/josw123/dart-fss-classifier): 재무제표 추출 성능 향상

## Usage

### Dart API Key 설정

-  [OPEN DART API 신청](https://opendart.fss.or.kr/)
-  환경 변수 DART_API_KEY 설정 또는 패키지 사용전 아래와 같이 설정

### Quick Starts

```python
import dart_fss as dart

# Open DART API KEY 설정
api_key='xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
dart.set_api_key(api_key=api_key)

# DART 에 공시된 회사 리스트 불러오기
corp_list = dart.get_corp_list()

# 삼성전자 검색
samsung = corp_list.find_by_corp_name('삼성전자', exactly=True)[0]

# 2012년부터 연간 연결재무제표 불러오기
fs = samsung.extract_fs(bgn_de='20120101')

# 재무제표 검색 결과를 엑셀파일로 저장 ( 기본저장위치: 실행폴더/fsdata )
fs.save()
```

## 주의사항

-   Open DART 및 DART 홈페이지의 경우 분당 100회 이상 요청시 서비스가 제한될 수 있음
-   [관련 공지사항](https://bit.ly/2wcnz2y>)

## License
This project is licensed under the MIT License

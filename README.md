# Dart-Fss
[![PyPI](https://img.shields.io/pypi/v/dart-fss.svg)](https://pypi.org/project/dart-fss/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dart-fss.svg)](https://pypi.org/project/dart-fss/)
[![Documentation](https://img.shields.io/badge/docs-readthedocs-blue.svg)](https://dart-fss.readthedocs.io/)
[![License](https://img.shields.io/pypi/l/dart-fss.svg)](LICENSE)

대한민국 금융감독원에서 운영하는 다트([DART](https://dart.fss.or.kr)) 사이트 크롤링 및 재무제표 추출을 위한 라이브러리

- Source code: https://github.com/josw123/dart-fss

## Features

-   [Open DART](https://opendart.fss.or.kr/)의 오픈 API를 이용한 전자공시 조회
-   [DART](https://dart.fss.or.kr)의 전자공시 정보를 이용한 재무제표 추출
-   XBRL 재무제표 분석 (일반 기업 및 은행·보험·증권·기타 금융업 서식 지원)

## Installation

- Open DART 지원 / 신규 Open DART API Key 필요
- Python 3.9 이상 지원
- Documentation: https://dart-fss.readthedocs.io/

``` bash
pip install -U dart-fss
```

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

-   Open DART API는 일일 이용한도가 있으며, DART 홈페이지는 짧은 시간에 요청이 몰리면 IP 접속이 일정 시간 차단될 수 있음
    -   [관련 공지사항](https://opendart.fss.or.kr/cop/bbs/selectArticleList.do?bbsId=B0000000000000000002): [FAQ]->[오픈API 이용한도는 어떻게 되나요?]
-   기본 요청 간격은 0.2초이며, 대량으로 조회할 경우 아래와 같이 간격을 늘리는 것을 권장

```python
import dart_fss as dart

# 요청 간격 1초로 변경
dart.utils.request.set_delay(1.0)
```

## License
This project is licensed under the MIT License

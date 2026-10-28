# Dart-Fss
[![PyPI](https://img.shields.io/pypi/v/dart-fss.svg)](https://pypi.org/project/dart-fss/)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/dart-fss.svg)](https://pypi.org/project/dart-fss/)
[![Downloads](https://static.pepy.tech/badge/dart-fss/month)](https://pepy.tech/project/dart-fss)
[![Documentation](https://img.shields.io/badge/docs-readthedocs-blue.svg)](https://dart-fss.readthedocs.io/)
[![License](https://img.shields.io/pypi/l/dart-fss.svg)](LICENSE)

대한민국 금융감독원에서 운영하는 다트([DART](https://dart.fss.or.kr)) 사이트 크롤링 및 재무제표 추출을 위한 라이브러리

- Source code: https://github.com/josw123/dart-fss
- Documentation: https://dart-fss.readthedocs.io/
- Releases: https://github.com/josw123/dart-fss/releases

## Features

-   [Open DART](https://opendart.fss.or.kr/)의 오픈 API를 이용한 전자공시 조회
-   [DART](https://dart.fss.or.kr)의 전자공시 정보를 이용한 재무제표 추출
-   여러 연도/분기 보고서의 재무제표를 하나의 DataFrame으로 병합
-   2012년 이후 XBRL 재무제표 분석, 이전 보고서 및 XBRL 미제공 보고서는 HTML 표 분석
-   XBRL 재무제표 분석 (일반 기업 및 은행·보험·증권·기타 금융업 서식 지원)
-   연결/별도, 연간/반기/분기, 누적/3개월 데이터 선택 추출
-   재무제표 엑셀 저장 및 불러오기

## Installation

- Open DART 지원 / 신규 Open DART API Key 필요
- Python 3.10 이상 지원

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

# 연결재무상태표 / 표시 깊이 지정
df_bs = fs['bs']
df_bs_depth1 = fs.show('bs', show_depth=1)

# 재무제표 검색 결과를 엑셀파일로 저장 ( 기본저장위치: 실행폴더/fsdata )
fs.save()
```

### 회사 검색

```python
# 고유번호 / 종목코드 / 회사명 / 업종 / 주요제품으로 검색
corp_list.find_by_corp_code('00126380')
corp_list.find_by_stock_code('005930')
corp_list.find_by_corp_name('삼성', exactly=False)
corp_list.find_by_sector('반도체')
corp_list.find_by_product('휴대폰')
```

### 공시 검색

```python
# 2019년부터 사업보고서 검색
reports = samsung.search_filings(bgn_de='20190101', pblntf_detail_ty='a001')

# 회사 미지정 검색 (최대 3개월, 페이지당 100건)
reports = dart.filings.search(bgn_de='20190101', end_de='20190331', page_count=100)
```

### 재무제표 추출 옵션

```python
# 2018년부터 연간 + 반기 + 분기 연결재무제표 불러오기
fs = samsung.extract_fs(
    bgn_de='20180101',
    report_tp='quarter',   # 'annual' 연간, 'half' 연간 + 반기, 'quarter' 연간 + 반기 + 분기
    separate=False,        # True: 별도재무제표
    lang='ko',             # 'en': 영문 label
    cumulative=False,      # True: 반기/분기 누적값만 추출
)

# 추출에 사용된 Label 정보
labels_bs = fs.labels['bs']

# 저장된 엑셀파일 불러오기
fs = dart.fs.FinancialStatement.load('fsdata/00126380_quarter.xlsx')
```

### 보고서 및 XBRL

```python
report = reports[0]

# 보고서 페이지 / 제목으로 페이지 검색 / 첨부파일
report.pages
report.find_all(includes='재무제표', scope=['pages'])
report.attached_files

# 리포트의 xbrl 데이터 (XBRL이 없거나 비어 있는 경우 None)
xbrl = report.xbrl

# 연결재무상태표 / 연결현금흐름표(분류 정보 제외) DataFrame 변환
df_bs = xbrl.get_financial_statement()[0].to_DataFrame()
df_cf = xbrl.get_cash_flows()[0].to_DataFrame(show_class=False)
```

### Open DART API

- Open DART 개발가이드의 API를 동일한 이름의 함수로 지원
- dart.api.filings / finance / info / issue / market / registration / shareholder

```python
# 단일회사 전체 재무제표 (2023년 사업보고서, 연결)
dart.api.finance.fnltt_singl_acnt_all(corp_code='00126380', bsns_year='2023', reprt_code='11011', fs_div='CFS')

# 최대주주 현황 / 임원·주요주주 소유보고
samsung.get_major_shareholder()
samsung.get_executive_shareholder()
```

### 속도 개선 옵션

- 여러 보고서 추출시 사용, 추출 결과는 기본 설정과 동일
- workers: XBRL 분석 병렬 처리 (다운로드는 순차 진행)
    - Windows/macOS에서 스크립트로 실행시 `if __name__ == '__main__':` 블록 안에서 호출 필요
- cache: 보고서별 분석 결과를 디스크에 저장, 재실행시 다운로드 및 분석 생략
    - 캐시된 보고서의 경우 분석 중 발생했던 경고는 다시 표시되지 않음

```python
# XBRL 분석 병렬 처리 (프로세스 4개)
fs = samsung.extract_fs(bgn_de='20120101', report_tp='quarter', workers=4)

# 분석 결과 캐시 사용 / 캐시 삭제
fs = samsung.extract_fs(bgn_de='20120101', cache=True)
dart.fs.clear_fs_cache()
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

-   추출된 재무제표는 공시 원문을 자동으로 분석한 결과로, 공시 서식 변경 및 정정 공시, 계정 병합 과정에 따라 원문과 다를 수 있음

## Contributing

-   버그 제보 및 기능 제안: [Issues](https://github.com/josw123/dart-fss/issues)
-   재무제표 추출 오류 제보시 회사 고유번호(corp_code), 접수번호(rcept_no), extract_fs 호출 인자 첨부
-   Pull Request 환영

```bash
# 네트워크 없이 실행되는 테스트
pip install -e . pytest
pytest dart_fss/tests/test_offline.py
```

## License
This project is licensed under the MIT License

-   금융감독원과 관련 없는 오픈소스 프로젝트로, DART 및 Open DART에서 공개적으로 제공하는 정보를 이용
-   데이터 이용시 [DART](https://dart.fss.or.kr) 및 [Open DART](https://opendart.fss.or.kr/) 이용약관 확인 필요

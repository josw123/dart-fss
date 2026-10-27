# -*- coding: utf-8 -*-

import os
import re
import math
import shutil
import tempfile
import warnings
import numpy as np
import pandas as pd
import traceback

from typing import Union, List, Dict, Tuple, Pattern, Optional
from collections import OrderedDict
from pandas import DataFrame
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from bs4.element import Tag

from dart_fss.api.filings import get_corp_info
from dart_fss.filings.reports import Report
from dart_fss.filings import search as search_filings
from dart_fss.utils import str_compare, str_unit_to_number_unit, is_notebook
from dart_fss.utils import str_insert_whitespace as ws
from dart_fss.errors.errors import NotFoundConsolidated, NoDataReceived
from dart_fss.utils import str_to_regex, get_currency_str
from dart_fss.fs.fs import FinancialStatement
from dart_fss.api.finance import download_xbrl
from dart_fss.filings.search_result import SearchResults


def str_to_float(text: str, unit: float) -> float:
    """ 문자를 float 데이터로 변환

    문자를 float 데이터로 변환, (1,000) 같은 경우 -1000 으로 변환

    Parameters
    ----------
    text: str
        입력문자
    unit: float
        unit for table
    Returns
    -------
    float
        변환된 숫자
    """
    regex = re.compile(r'\((-*\d+)\)|\(-\)(\d+)')  # 음수 처리를 위한 정규식
    regex_korean = re.compile(r'[ㄱ-힣]|[a-zA-Z]')
    if isinstance(text, str):
        try:
            text = re.sub(r',|\s+', '', text)
            if regex_korean.search(text):
                value = float(regex_korean.sub('', text))
                # Value 값에 단위가 들어간 경우 unit으로 나누어 이후 계산에서 일괄적으로 곱해질 unit 값을 제거한다
                if re.search('원', text):
                    return value / unit
                else:
                    return value
            if regex.search(text):
                value = regex.search(text).group(1)
                if value is None:
                    value = regex.search(text).group(2)
                return -float(value)
            else:
                return float(text)
        except (ValueError, TypeError):
            return 0.0
    elif isinstance(text, (int, float)):
        return float(text)
    else:
        raise ValueError('Invalid Value: {}'.format(text))


regex_br = re.compile(r'<br\s*?\/?\s*?>')


def text_split_by_br(tag) -> list:
    s = regex_br.sub('\n', str(tag),  re.MULTILINE)
    t = BeautifulSoup(s, 'html.parser')
    s = t.get_text()
    res = [x for x in s.split('\n') if len(x) > 0]
    return res


def get_datetime(year, month, day):
    try:
        return datetime(year, month, day)
    except ValueError:
        if month not in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]:
            warnings_text = "Month must be in 1..12"
            warnings.warn(warnings_text, RuntimeWarning)
            return None
        if day != 0:
            if month == 12:
                dt = datetime(year + 1, 1, 1)
            else:
                dt = datetime(year, month + 1, 1)
            dt = dt - relativedelta(day=1)
        else:
            dt = datetime(year, month, 1)
        warnings_text = "Day({0}.{1}.{2}) is out of range for month. dart-fss tries to fix {0}.{1}.{2} to {0}.{1}.{3}".format(
            year, month, day, dt.day)
        warnings.warn(warnings_text, RuntimeWarning)
        return dt


def extract_date_from_header(header):
    """ 재무제표 기간 추출을 위해 사용하는 method"""
    # YYYY년 MM월 DD일 형태 검색
    regex = re.compile(
        r'(\d{4})[^0-9:]*\s*(\d{1,2})[^0-9]*\s*(\d{1,2})')  # Exclude ':'
    # YYYY년 MM월 DD일 M'M'월 D'D'일 형태 검색
    regex2 = re.compile(
        # Exclude ':'
        r'(\d{4})[^0-9:]*\s*(\d{1,2})[^0-9]*\s*(\d{1,2})[^0-9]*\s*(\d{1,2})[^0-9]*\s*(\d{1,2})')
    date_info = []
    td_list = header.find_all('td')
    re_nbsp = re.compile(r'\xa0')
    re_space = re.compile(r'\s+')
    for td in td_list:
        # Remove white text in tag
        for tag in td.find_all(style=re.compile(r'color:#ffffff', re.IGNORECASE)):
            tag.decompose()
        texts = text_split_by_br(td)
        for text in texts:
            text = re_nbsp.sub(' ', text)
            text = re_space.sub(' ', text)
            searched = regex.findall(text)
            searched2 = regex2.findall(text)

            # 잘못된 Table Header 검색시 필터링
            searched_length = len(searched)
            if len(text) > searched_length * 80:
                continue
            elif searched_length > 0:
                f = searched[0]
                if len(searched2) == 0:
                    # 오류 방지를 위해 Dummy 값 삽입
                    searched2 = [[9999, 99, 99, 99, 99]]
                s = searched2[0]
                # 만약 regex와 regex2의 첫번째 결과 값이 동일할때 regex2로 검색처리
                # 제21(당)기 2018년 01월 01일부터 12월 31일 까지 형태 처리
                if f[1] == s[1] and f[2] == s[2] and int(s[3]) < 13 and int(s[4]) < 32:
                    date = []

                    year = int(s[0])
                    month = int(s[1])
                    day = int(s[2])

                    dt = get_datetime(year, month, day)
                    if dt is not None:
                        date.append(dt)

                    month = int(s[3])
                    day = int(s[4])
                    dt = get_datetime(year, month, day)
                    if dt is not None:
                        date.append(dt)

                    if len(date) > 0:
                        date_info.append(tuple(date))
                else:
                    date = []
                    for d in searched:
                        year = int(d[0])
                        month = int(d[1])
                        day = int(d[2])

                        dt = get_datetime(year, month, day)
                        if dt is not None:
                            date.append(dt)

                    if len(date) > 0:
                        date_info.append(tuple(date))

    return date_info


def extract_unit_from_header(header):
    """ html에서 unit을 추출하는 함수 """
    unit_regex = re.compile(r'\(단위\s*?:\s*(.*)\)')
    td_list = header.find_all('td')
    for td in td_list:
        searched = unit_regex.search(td.text)
        if searched:
            return searched.group(1)

    return '원'


def convert_thead_into_columns(fs_tp: str, fs_table: dict, separate: bool = False,
                               lang: str = 'ko'):
    """ thead에서 DataFrame의 columns을 추출하는 Method"""
    def column_ko_to_en(ko):
        ko_to_en = {
            '과목': 'label_ko',
            '주석': 'comment'
        }
        en = ko_to_en.get(ko)
        return en if en else ko

    thead = fs_table['table'].thead

    if thead is None:
        tt = fs_table['table'].tbody.tr.extract()
        thead = BeautifulSoup('<thead></thead>', 'html.parser')
        thead.thead.append(tt)
        for td in thead.tr.find_all('td'):
            td.name = 'th'
    th_colspan_list = [int(th.attrs.get('colspan', 1))
                       for th in thead.tr.find_all('th')]
    date_info = extract_date_from_header(fs_table['header'])
    # 검색된 날짜가 없을경우 Empty array return
    if len(date_info) == 0:
        return []
    # Regular Expression for title
    regex = str_to_regex('과목 OR 주석')

    fs_string = {
        'bs': 'Statement of financial position',
        'is': 'Income statement',
        'cis': 'Statement of comprehensive income',
        'cf': 'Statement of cash flows'
    }

    str_unit = extract_unit_from_header(fs_table['header'])
    str_unit = get_currency_str(str_unit)
    if str_unit:
        for key in fs_string:
            fs_string[key] = fs_string[key] + '(Unit: {})'.format(str_unit)

    label = {
        'ko': {
            True: '별도재무제표',
            False: '연결재무제표'
        },
        'en': {
            True: 'Separate',
            False: 'Consolidated'
        }
    }

    # 최대 Col
    col_length = sum(th_colspan_list)
    # 최대 Row
    row_length = len(thead.find_all('tr'))
    row_length = row_length + 1 if row_length == 1 else row_length
    # row-sapn, col-span을 처리하기 위한 Matrix
    columns_matrix = [[None for _y in range(
        col_length)] for _x in range(row_length)]

    # Bug fix (#141): Return an empty array if a duplicate column exists
    duplicate_check = []

    for idx, tr in enumerate(thead.find_all('tr')):
        start_idx = 0
        for ele_idx, element in enumerate(columns_matrix[idx]):
            if element is None:
                start_idx = ele_idx
                break

        for jdx, th in enumerate(tr.find_all('th')):
            row_span = int(th.attrs.get('rowspan', 1))
            col_span = int(th.attrs.get('colspan', 1))
            text = re.sub(r'\s+', '', th.text)
            # Bug fix (#141): Return an empty array if a duplicate column exists
            if text in duplicate_check:
                return []
            duplicate_check.append(text)
            # Fix bug(#76)
            # 첫 행의 첫 칸(과목)은 비어 있어도 아래에서 '과목'으로 처리 (빈 칸으로 건너뛰면 열이 밀림)
            if len(text) == 0 and not (idx == 0 and jdx == 0):
                continue
            date_list = [datetime(1900, 1, 1)]
            if idx == 0:
                if jdx == 0:
                    text = '과목'
                elif regex.search(text) is None:
                    if len(date_info) > 0:
                        date_list = date_info.pop(0)
                    else:
                        date = '-'.join([date.strftime('%Y%m%d')
                                        for date in date_list])
                        warnings_text = "Date data length does not match table header."\
                            + "So last date was set using last data({}). ".format(date)
                        warnings.warn(warnings_text, RuntimeWarning)
                    text = '-'.join([date.strftime('%Y%m%d')
                                    for date in date_list])

            if regex.search(text):
                row_span = 2

            for mdx in range(row_span):
                for ndx in range(col_span):
                    new_text = text
                    if mdx == 0 and regex.search(text):
                        new_text = fs_string[fs_tp]
                    columns_matrix[idx + mdx][start_idx + ndx] = new_text
            start_idx = start_idx + ndx + 1
    # Bug fix (#141): Return an empty array if a duplicate '과목' exists
    if len(columns_matrix) < 2 or columns_matrix[1].count('과목') > 1:
        return []

    regex_3month = re.compile(r'3개월')
    regex_total = str_to_regex(r'누적 OR 금액')

    columns = []

    for jdx in range(len(columns_matrix[0])):
        column = []
        sec_item = []
        for idx in range(len(columns_matrix)):
            item = columns_matrix[idx][jdx]
            if idx == 0:
                column.append(item)
                continue
            elif idx == 1 and (item is None or regex.search(item) is None):
                sec_item.append(label[lang][separate])
            else:
                pass

            if item is None:
                pass
            elif str_compare(column[0], item):
                continue
            elif regex_3month.search(item):
                # extract date info
                date_info = [datetime.strptime(
                    date_str, '%Y%m%d') for date_str in column[0].split('-')]

                # calculating start_dt
                delta = relativedelta(months=3)
                start_dt = date_info[1] - delta
                start_dt = start_dt.replace(day=1)

                end_dt = date_info[1]
                column[0] = '-'.join([date.strftime('%Y%m%d')
                                     for date in [start_dt, end_dt]])
            elif regex_total.search(item):
                pass
            else:
                sec_item.append(column_ko_to_en(item))
        if sec_item[0] in ['label_ko', 'comment']:
            column.append(sec_item[0])
        else:
            column.append(tuple(sec_item))
        columns.append(column)
    return columns


def convert_tbody_to_dataframe(columns: list, fs_table: dict):
    """ Html의 tbody를 DataFrame으로 변환하는 함수"""
    column_matrix = OrderedDict()
    for idx, column in enumerate(columns):
        key = tuple(column)
        if column_matrix.get(key):
            column_matrix[key].append(idx)
        else:
            column_matrix[key] = []
            column_matrix[key].append(idx)
    deduplicated = [key for key in column_matrix]

    df_columns = pd.MultiIndex.from_tuples(deduplicated)
    df_column_list = df_columns.tolist()

    tbody = fs_table['table'].tbody
    regex = str_to_regex('label_ko OR comment')
    str_unit = extract_unit_from_header(fs_table['header'])
    unit = str_unit_to_number_unit(str_unit)
    unit_regex = re.compile(r'\(단위\s*?:\s*([a-zA-Zㄱ-힣])\)')

    # br 태그에 의해 구분되는 경우 처리하기 위한 함수
    def get_text_before_newline(tag):
        br = tag.find('br')
        if br is None:
            # br 태그가 없을시 단순 반환
            return tag.text
        else:
            text = ''
            for x in br.previous_siblings:
                text += str(x)
            # br 태그로 구분되는 경우 첫번째 라인 텍스트만 반환
            return BeautifulSoup(text, 'html.parser').text

    rows = []
    for tr in tbody.find_all('tr'):
        extracted = [re.sub(r'\s+|=+', '', get_text_before_newline(td))
                     for td in tr.find_all('td')]
        row = {key: 0 for key in deduplicated}
        for key, index_list in column_matrix.items():
            for index in index_list:
                if len(extracted) <= index:
                    row[key] = None
                elif isinstance(key[1], str):
                    row[key] = extracted[index]
                elif regex.search(' '.join(key[1])):
                    value = extracted[index]
                    row[key] = value
                else:
                    value = str_to_float(extracted[index], unit)
                    row[key] += value

            if isinstance(row[key], float):
                if abs(row[key]) < 1e-10:
                    row[key] = ''
                else:
                    row[key] = row[key] * unit

        ordered_list = [row.get(column, None) for column in df_column_list]

        try:
            if len(ordered_list) > 0 and ordered_list[0] is not None:
                row_unit = unit_regex.search(ordered_list[0])
            else:
                row_unit = False
        except TypeError as ex:
            warnings_text = '{} : {}'.format(repr(ex), ordered_list[0])
            warnings.warn(warnings_text, RuntimeWarning)
            row_unit = False

        if row_unit:
            row_unit = str_unit_to_number_unit(row_unit.group(1))
            for jdx, value in enumerate(ordered_list):
                if isinstance(value, str):
                    pass
                else:
                    ordered_list[jdx] = ordered_list[jdx] / unit * row_unit

        rows.append(ordered_list)

    # 행 단위 df.loc[idx] 추가는 O(n^2)이고 pandas 4에서 dtype 불일치 시 오류가 발생하므로 한 번에 생성
    if not rows:
        return pd.DataFrame(columns=df_columns)
    return pd.DataFrame(rows, columns=df_columns, index=pd.Index(np.arange(len(rows)), dtype='int64'))


def seek_table(tables: List, includes: Pattern,
               excludes: Union[Pattern, None] = None) -> Tuple[Union[str, None], Union[str, None], Union[str, None]]:
    """ Table 검색 """
    # 날짜 검색을 위한 Regular Expression
    regex = re.compile(r'\d{4}(.*?)\d{1,2}(.*?)\d{1,2}')

    # Header Tag 가 아닌 경우 저장
    not_headers = []

    # Minimum Row Number
    MIN_ROW_NUMBER = 4

    for table in tables:
        # Table 의 Row 가 4개 이하인 경우 재무제표 테이블이 아닌것으로 판정
        rows = table.find_all('tr')
        if len(rows) < MIN_ROW_NUMBER:
            continue

        for tag in table.previous_siblings:
            # tag 가 tables 에 있으면 검색 종료
            if tag in tables:
                break
            # tag 가 Tag Object 인 경우에만 검색 진행
            if isinstance(tag, Tag):
                # title 검색
                children = tag.find_all(string=includes)
                if len(children) == 0:  # 부국증권도 사업보고서 검색 안되던 문제 해결을 위한 코드(#66)
                    texts = text_split_by_br(tag)
                    children = [
                        text for text in texts if includes.search(text)]

                for child in children:
                    title = child
                    if title:
                        title = re.sub(r'\s+', '', title)
                        # 만약 타이틀에 제외될 단어 포함시 Pass
                        if excludes and excludes.search(title):
                            not_headers.append(tag)
                            continue

                        # 타이틀이 너무 길때 Pass
                        # len(title) > 12 일때 일부 회사(메리츠화재)에서 연결포괄손익계산서 검색이 안되는 문제가 발생
                        if len(title) > 13:
                            not_headers.append(tag)
                            continue

                        headers = table.find_all_previous('table', class_='nb')
                        for header in headers:

                            # Header 가 None 이거나 not_headers 에 포함된 경우 Pass
                            if header is None or header in not_headers:
                                continue

                            # Row 가 2개 이하인 경우 Pass
                            tr_list = header.find_all('tr')
                            if len(tr_list) < 2:
                                continue

                            # 검색된 날짜가 한개도 없을 경우 Pass
                            datetime_cnt = 0
                            for tr in tr_list:
                                if regex.search(tr.text):
                                    datetime_cnt += 1

                            if datetime_cnt == 0:
                                continue

                            return title, header, table

    return None, None, None


def search_fs_table(tables: List, fs_tp: Tuple[str] = ('bs', 'is', 'cis', 'cf'),
                    separate: bool = False) -> Dict[str, dict]:
    """
    페이지의 재무제표 테이블을 검색하는 함수

    Parameters
    ----------
    tables: list of ResultSet
        page 내부에서 검색된 모든 Tables
    fs_tp: tuple of str
        'bs' 재무상태표, 'is' 손익계산서, 'cis' 포괄손익계산서, 'cf' 현금흐름표
    separate: bool
        개별 재무제표 여부

    Returns
    -------
    dict of {str : dict }
        검색된 재무제표 결과
    """
    fs_table = OrderedDict()

    # 순서대로 검색 (순서 변경 금지)
    queryset = {
        'bs': ws('재무상태표') + ' OR ' + ws('대차대조표'),
        'is': ws('손익계산서'),
        'cis': ws('포괄손익계산서'),
        'cf': ws('현금흐름표'),
    }

    for key, query in queryset.items():
        if key not in fs_tp:
            continue

        # 연결재무제표 검색시 사용할 query 구문
        excludes = None
        if not separate:
            query = query + ' AND ' + ws('연결')
        else:
            excludes = ws('연결')

        if key == 'is':
            if excludes:
                excludes += ' OR ' + ws('포괄')
            else:
                excludes = ws('포괄')

        if excludes:
            excludes = str_to_regex(excludes)

        regex = str_to_regex(query)
        title, header, tb = seek_table(
            tables=tables, includes=regex, excludes=excludes)
        fs_table[key] = {'title': title, 'header': header, 'table': tb}
    return fs_table


def extract_fs_table(fs_table, fs_tp, separate: bool = False, lang: str = 'ko', report=None):
    results = OrderedDict()
    for tp, table in fs_table.items():
        if tp in fs_tp:
            df = None
            if table['table']:
                try:
                    columns = convert_thead_into_columns(
                        fs_tp=tp, fs_table=table, separate=separate, lang=lang)
                    # Table Header 가 추출된 경우에만 Table Body 추출
                    if len(columns) > 0:
                        df = convert_tbody_to_dataframe(
                            columns=columns, fs_table=table)
                except Exception as ex:
                    traceback.print_exc()
                    report_dict = None
                    if report is not None:
                        report_dict = report.to_dict()
                    warnings_text = 'Unable to extract a {} type financial statement. : {}'.format(
                        tp, report_dict)
                    warnings.warn(warnings_text, RuntimeWarning)
            results[tp] = df
    return results


def report_find_all(report: Report, query: dict, fs_tp: Tuple[str], separate: bool) -> Tuple[int, Dict[str, Dict]]:
    """
    Report의 Page 중 Query 조건에 맞는 페이지 검색후 모든 재무제표 Table 추출

    Parameters
    ----------
    report: Report
        Report
    query: dict
        검색 조건
    fs_tp:  tuple of str
        검색할 재무제표 타입
    separate: bool
        개별 재무제표 여부

    Returns
    -------

    """
    count = 0
    fs_table = None
    searched_end = False
    searched = report.find_all(**query)

    for key in searched:
        for page in searched[key]:
            non_break_space = u'\xa0'
            html = page.html.replace(non_break_space, ' ')
            soup = BeautifulSoup(html, 'html.parser')

            tables = soup.find_all('table', border='1')
            fs_table = search_fs_table(
                tables=tables, fs_tp=fs_tp, separate=separate)
            count = sum([fs_table[fs_tp]['table']
                        is not None for fs_tp in fs_table])
            if count > 0:
                searched_end = True
                break
        if searched_end:
            break
    return count, fs_table


def analyze_html(report: Report, fs_tp: Tuple[str] = ('bs', 'is', 'cis', 'cf'),
                 lang: str = 'ko', separate: bool = False) -> Union[Dict[str, DataFrame], None]:
    """
    보고서의 HTML을 이용하여 재무제표를 추출하는 Method

    Parameters
    ----------
    report: Report
        리포트
    fs_tp: tuple of str
        'bs' 재무상태표, 'is' 손익계산서, 'cis' 포괄손익계산서, 'cf' 현금흐름표
    lang: str
        'ko': 한글 / 'en' 영문
    separate: bool
        개별 재무제표 여부

    Returns
    -------
    dict of {str: DataFrame}
        재무제표
    """

    inc = ['재무제표', '감사보고서']
    exc = ['주석', '결합', '의견', '수정', '검토보고서']

    includes = ' OR '.join([ws(x) for x in inc])
    excludes = ' OR '.join([ws(x) for x in exc])

    query = {
        'includes': includes,
        'excludes': excludes,
        'scope': ['attached_reports', 'pages'],
        'options': {'title': True}  # 첨부보고서 및 연결보고서의 title 까지 검색
    }

    if separate:
        query['excludes'] += ' OR ' + ws('연결')
    else:
        query['includes'] += ' AND ' + ws('연결')

    count, fs_table = report_find_all(report, query, fs_tp, separate)

    # 검색결과가 없을시 재검색, 검색 키워드 변경
    if count == 0:
        query = {
            'includes': r'재무제표 OR 명세서',
            'excludes': r'주석 OR 결합 OR 의견 OR 수정 OR 검토보고서',
            'scope': ['attached_reports', 'pages']
        }
        count, fs_table = report_find_all(report, query, fs_tp, separate)

    # 수정된 검색어의 경우에도 검색결과가 없을시, None 반환
    if count == 0:
        return None

    extract_results = extract_fs_table(
        fs_table=fs_table, fs_tp=fs_tp, separate=separate, lang=lang, report=report)
    return extract_results


def find_all_columns(df: DataFrame, query: str) -> pd.Index:
    """
    DataFrame의 column을 검색어를 통해 검색하는 함수

    Parameters
    ----------
    df: DataFrame
        검색할 DataFrame
    query: str
        검색어

    Returns
    -------
    tuple of str
        검색된 DataFrame의 column
    """
    regex = str_to_regex(query)
    if df is None:
        return []
    columns = df.columns.tolist()

    results = []
    for column in columns:
        for item in column:
            if isinstance(item, str) and regex.search(item):
                results.append(column)
            else:
                if regex.search(' '.join(item)):
                    results.append(column)
    if len(results) > 0:
        results = pd.MultiIndex.from_tuples(results)
    return results


def extract_account_title(title):
    title = title.split('.')
    if len(title) == 1:
        title = title[0]
    elif len(title) > 1:
        title = ''.join(title[1:])
    title = re.sub(r'\[.*?\]|\(.*?\)|<.*?>|[^가-힣|a-z|A-Z]', '', title)
    title = re.sub(r'\s+', '', title)
    return title


def compare_df_and_ndf_label_and_concept(column: Tuple[Union[str, Tuple[str]]],
                                         df: DataFrame, ndf: DataFrame, ldf: DataFrame,
                                         ndata: List[Union[float, str, None]],
                                         nlabels: List[str]) -> Tuple[List[Union[float, str]], List[str]]:
    """
    Labels 을 시용하여 데이터를 검색하는 함수

    Parameters
    ----------
    column: tuple
        추가할 column Name
    df: dict of { str: DataFrame }
        데이터를 추가할 DataFrame
    ndf: dict of { str: DataFrame }
        데이터를 검색할 DataFrame
    ldf: dict of { str: DataFrame }
        Label DataFrame
    ndata: list of float
        추가할 column의 데이터 리스트
    nlabels: list of str
        추가할 column의 label 리스트

    Returns
    -------
    tuple of list
        추가할 column의 데이터 리스트, 추가할 column의 label 리스트
    """
    label_none_data = []
    df_label_column = find_all_columns(df, 'label_ko')[0]
    ndf_label_column = find_all_columns(ndf, 'label_ko')[0]

    concept_none_data = {}
    df_concept_column = find_all_columns(df, 'concept_id')
    ndf_concept_column = find_all_columns(ndf, 'concept_id')

    # concept_id 컬럼이 존재하는지 여부 조사
    concept_exist = len(df_concept_column) * len(ndf_concept_column) != 0
    if concept_exist:
        df_concept_column = df_concept_column[0]
        ndf_concept_column = ndf_concept_column[0]

    en_none_data = {}
    df_en_column = find_all_columns(df, 'label_en')
    ndf_en_column = find_all_columns(ndf, 'label_en')

    # label_en 컬럼이 존재하는지 여부 조사
    en_exist = len(df_en_column) * len(ndf_en_column) != 0
    if en_exist:
        df_en_column = df_en_column[0]
        ndf_en_column = ndf_en_column[0]

    for idx, value in enumerate(ndata):
        if isinstance(value, str):
            # 이전에 검색된 데이터가 문자인 경우 pass
            pass
        elif value is None:
            # 이전에 검색된 데이터가 없는 경우 pass
            pass
        elif math.isnan(value):
            # 이전에 검색된 데이터가 유효한 값이 아닌 경우 pass
            pass
        else:
            # 올바른 값이 경우 검색 X
            continue

        # label 추출
        label = df[df_label_column].iloc[idx]
        label = re.sub(r'\s+', '', label)
        label = extract_account_title(label)
        label_set = set(ldf.iloc[idx])
        label_set.add(label)
        # (index, label_set) 리스트 생성
        label_none_data.append((idx, label_set))

        # concept_id가 존재하는 경우 concept_id도 추가로 검색
        if concept_exist:
            concept = df[df_concept_column].iloc[idx]
            concept_none_data[concept] = idx

        # label_en가 존재하는 경우 label_en도 추가로 검색
        if en_exist:
            en = df[df_en_column].iloc[idx]
            en_none_data[en] = idx

    # 기존 Dataframe index 중 사용된 결과 값 리스트
    used = []

    for idx in range(len(ndf)):
        # 검색된 값
        value_found = None
        # 검색된 기존 Dataframe 의 index
        index_found = None

        # 검색할 label 명
        label = extract_account_title(ndf[ndf_label_column].iloc[idx])

        if concept_exist:
            # 추가할 Dataframe 의 concept_id
            concept = ndf[ndf_concept_column].iloc[idx]
            index_found = concept_none_data.get(concept)
            if index_found in used:
                continue
            elif index_found is not None:
                value_found = ndf[column].iloc[idx]

        if index_found is None:
            if en_exist:
                en = ndf[ndf_en_column].iloc[idx]
                index_found = en_none_data.get(en)
                if index_found in used:
                    continue
                elif index_found is not None:
                    value_found = ndf[column].iloc[idx]

        if index_found is None:
            for index, label_set in label_none_data:
                if index in used:
                    continue
                if label in label_set:
                    value_found = ndf[column].iloc[idx]
                    index_found = index
                    break

        if index_found is None:
            pass
        elif isinstance(index_found, int):
            used.append(index_found)
            ndata[index_found] = value_found
            nlabels[index_found] = label

    return ndata, nlabels


def compare_df_and_ndf_value(column: Tuple[Union[str, Tuple[str]]],
                             df: DataFrame, ndf: DataFrame, ldf: DataFrame,
                             ndata: List[Union[float, str, None]],
                             nlabels: List[str]) -> Tuple[List[Union[float, str]], List[str]]:
    """
    중복된 데이터의 값을 비교하여 데이터 값을 추출하는 함수

    Parameters
    ----------
    column: tuple
        추가할 column Name
    df: dict of { str: DataFrame }
        데이터를 추가할 DataFrame
    ndf: dict of { str: DataFrame }
        데이터를 검색할 DataFrame
    ldf: dict of { str: DataFrame }
        Label DataFrame
    ndata: list of float
        추가할 column의 데이터 리스트
    nlabels: list of str
        추가할 column의 label 리스트

    Returns
    -------
    tuple of list
        추가할 column의 데이터 리스트, 추가할 column의 label 리스트
    """
    _, df_columns = split_columns_concept_data(df.columns)
    _, ndf_columns = split_columns_concept_data(ndf.columns)

    # set 순회 순서는 문자열 해시(실행마다 무작위)에 따라 달라져 동일 개수로 매칭된 행 중 선택 결과가 바뀌므로
    # 기존 Dataframe의 column 순서를 유지
    overlap = ordered_intersection(df_columns, ndf_columns)
    nko_column = find_all_columns(ndf, r'label_ko')

    for idx, value in enumerate(ndata):
        if isinstance(value, str):
            # 이전에 검색된 데이터가 문자인 경우 pass
            pass
        elif value is None:
            # 이전에 검색된 데이터가 없는 경우 pass
            pass
        elif math.isnan(value):
            # 이전에 검색된 데이터가 유효한 값이 아닌 경우 pass
            pass
        else:
            # 올바른 값이 경우 검색 X
            continue

        nvalue = None
        nlabel = ''

        found = {}
        found_sign = {}
        max_found = 0

        check_all_zeros = pd.to_numeric(
            df[list(overlap)].iloc[idx], errors='coerce').sum()
        if check_all_zeros == 0.0:
            continue  # 모든 값이 0인 경우 pass

        for col in overlap:
            value = df[col].iloc[idx]
            if isinstance(value, str):
                pass
            elif value is None:
                pass
            elif math.isnan(value):
                pass
            else:
                sign = 1
                # Ref와 일치하는 값을 가지는 row index 찾기
                w = ndf[ndf[col] == value].dropna(
                    axis=1, how='all').dropna(how='all')
                # 만약 찾지 못하는 경우 Ref의 값의 음수와 동일한 값을 가지는 row index 찾기
                if len(w) == 0:
                    sign = -1
                    w = ndf[ndf[col] == -
                            value].dropna(axis=1, how='all').dropna(how='all')

                if len(w) > 0:
                    for index in w.index.values:
                        found[index] = found.get(index, 0) + 1
                        max_found = max(max_found, found[index])
                        found_sign[index] = sign

        for k, v in found.items():
            if v >= max_found:
                nvalue = found_sign[k] * ndf[column].iloc[k]
                nlabel = ndf[nko_column].iloc[k].iloc[0]
                nlabel = extract_account_title(nlabel)

        if nvalue and math.isnan(nvalue):
            nvalue = None

        ndata[idx] = nvalue
        nlabels[idx] = nlabel
    return ndata, nlabels


additional_comparison_function = [compare_df_and_ndf_value]


def init_label(fs_df: Dict[str, DataFrame],
               fs_tp: Tuple[str] = ('bs', 'is', 'cis', 'cf'),
               label_df: Dict[str, DataFrame] = None):
    """ 각각의 타입에 따라 추출된 Label들을 담고 있는 Dataframe 초기화

    Parameters
    ----------
    fs_df: dict of {str: DataFrame}
        추출된 재무제표
    fs_tp: tuple of str, optional
        'bs' 재무상태표, 'is' 손익계산서, 'cis' 포괄손익계산서, 'cf' 현금흐름표
    label_df: dict of {str: DataFrame}
        초기화할 label_df

    Returns
    -------
    dict of {str : DataFrame}
        초기화된 label_df
    """
    if label_df is None:
        label_df = {tp: None for tp in fs_tp}

    for tp in fs_df:
        if tp in fs_tp:
            # 추가될 재무제표의 DataFrame
            df = fs_df[tp]
            if df is None:
                continue
            # label_df가 없을시 초기화
            if label_df.get(tp) is None:
                concept_column = find_all_columns(df, r'concept_id')
                ko_column = find_all_columns(df, r'label_ko')
                # Label_ko 가 없을시 Table 오류 이므로 None 처리
                if len(ko_column) == 0:
                    fs_df[tp] = None
                    continue
                else:
                    ko_column = ko_column[0]
                date_columns = find_all_columns(df, r'\d{8}')

                label_columns = []
                if len(concept_column) == 1:
                    label_columns.append(('default', 'concept_id',))
                for column in date_columns:
                    label_columns.append(column)
                nlabel_columns = pd.MultiIndex.from_tuples(label_columns)
                label_df[tp] = pd.DataFrame(columns=nlabel_columns)

                if len(concept_column) == 1:
                    label_df[tp][nlabel_columns[0]] = [
                        extract_account_title(x) for x in list(df[concept_column[0]])]

                for column in date_columns:
                    label_df[tp][column] = list(df[ko_column])
    return label_df


def merge_fs(fs_df: Dict[str, DataFrame],
             nfs_df: Dict[str, DataFrame],
             label_df: Dict[str, DataFrame],
             fs_tp: Tuple[str] = ('bs', 'is', 'cis', 'cf'),
             min_required: int = 4) -> Tuple[Dict[str, DataFrame], Dict[str, DataFrame]]:
    """
    재무제표 DataFrame과 Report의 데이터를 합쳐주는 Method

    Parameters
    ----------
    fs_df: dict of {str: DataFrame}
        데이터를 추가할 DataFrame
    nfs_df: dict of {str: DataFrame}
        새로운 데이터를 검색할 DataFrame
    label_df: dict of {str: DataFrame}
        재무제표 검색결과시 추출된 값의 Label
    fs_tp: tuple of str, optional
        'bs' 재무상태표, 'is' 손익계산서, 'cis' 포괄손익계산서, 'cf' 현금흐름표
    min_required: int, optional
        Merge를 위한 최소한의 데이터 개수
    Returns
    -------
    tuple of dict of {str: DataFrame}
        재무제표, 추출된 Label 리스트
    """
    global additional_comparison_function

    for tp in fs_df:
        if tp in fs_tp:
            # 추가될 재무제표의 DataFrame
            df = fs_df[tp]

            # 새로 추가할 재무제표
            ndf = nfs_df[tp]

            # 재무제표가 없을시 추가 검색 X
            if df is None:
                if ndf is None:
                    continue
                else:
                    fs_df[tp] = ndf.copy(deep=True)
                    df = fs_df[tp]

            # 검색된 재무제표가 없을시 추가 검색 X
            if ndf is None:
                continue

            # label_df가 없을시 초기화
            if label_df.get(tp) is None:
                label_df = init_label(
                    fs_df=fs_df, fs_tp=fs_tp, label_df=label_df)

            _, df_columns = split_columns_concept_data(df.columns)
            _, ndf_columns = split_columns_concept_data(ndf.columns)
            # set 순회 순서는 실행마다 달라지므로 추가할 Dataframe의 column 순서를 유지
            df_columns = convert_multiindex_to_set(df_columns)

            date_regex = re.compile(r'\d{8}')
            diff = [x for x in ordered_columns(ndf_columns)
                    if x not in df_columns and date_regex.search(x[0])]
            diff.sort(key=lambda x: date_regex.findall(x[0])[0], reverse=True)

            # Data가 동일할 경우 Continue
            if len(diff) == 0:
                continue

            diff = pd.MultiIndex.from_tuples(diff)
            for column in diff:
                ndata = [None for _ in range(len(df))]
                nlabels = ['' for _ in range(len(df))]

                ndata, nlabels = compare_df_and_ndf_label_and_concept(
                    column, df, ndf, label_df[tp], ndata, nlabels)

                for compare_func in additional_comparison_function:
                    ndata, nlabels = compare_func(
                        column, df, ndf, label_df[tp], ndata, nlabels)

                ndata = pd.to_numeric(ndata, errors='coerce')
                count = np.count_nonzero(~np.isnan(ndata))

                if count < min_required:  # ndata의 유효한 값이 min_required 이하인 경우 추가 Merge X
                    continue

                label_df[tp][column] = nlabels
                fs_df[tp][column] = ndata

    return fs_df, label_df


def convert_multiindex_to_set(multiindex):
    if multiindex is None:
        return set()
    return set(multiindex.tolist())


def ordered_columns(multiindex) -> list:
    """ 중복을 제거한 column 리스트 (순서 유지)"""
    if multiindex is None:
        return []
    return list(dict.fromkeys(multiindex.tolist()))


def ordered_intersection(multiindex, other) -> list:
    """ multiindex의 순서를 유지한 교집합"""
    other = convert_multiindex_to_set(other)
    return [x for x in ordered_columns(multiindex) if x in other]


def analyze_xbrl(report, fs_tp: Tuple[str] = ('bs', 'is', 'cis', 'cf'), separate: bool = False, lang: str = 'ko',
                 show_abstract: bool = False, show_class: bool = True, show_depth: int = 10,
                 show_concept: bool = True, separator: bool = True) -> Union[Dict[str, DataFrame], None]:
    """
    Report의 xbrl 파일 분석을 통한 재무제표 추출

    Parameters
    ----------
    report: Report
        Report
    fs_tp: tuple of str, optional
        'bs' 재무상태표, 'is' 손익계산서, 'cis' 포괄손익계산서, 'cf' 현금흐름표
    separate: bool, optional
        개별재무제표 여부
    lang: str, optional
        'ko' 한글, 'en' 영문
    show_abstract: bool, optional
        Abstract 행 표시 여부
    show_class: bool, optional
        class 표시 여부
    show_depth: int, optional
        표시할 class 깊이
    show_concept: bool, optional
        concept_id 표시여부
    separator: bool, optional
        1000단위 구분자 표시 여부

    Returns
    -------
    dict of {str : DataFrame} or None
        pandas DataFrame
    """

    xbrl = report.xbrl
    if xbrl is None:
        return None

    # 재무제표 추출을 위한 함수
    def get_fs():
        data = xbrl.get_financial_statement(separate=separate)
        return data[0] if data else None

    def get_is():
        data = xbrl.get_income_statement(separate=separate)
        if data:
            data = data[0] if len(data) > 1 else None
        return data

    def get_ci():
        data = xbrl.get_income_statement(separate=separate)
        if data:
            data = data[1] if len(data) > 1 else data[0]
        return data

    def get_cf():
        data = xbrl.get_cash_flows(separate=separate)
        return data[0] if data else None

    func_fs = {
        'bs': get_fs,
        'is': get_is,
        'cis': get_ci,
        'cf': get_cf,
    }

    # DataFrame 옵션
    option = {
        'label': 'Separate' if separate else 'Consolidated',
        'lang': lang,
        'show_abstract': show_abstract,
        'show_class': show_class,
        'show_depth': show_depth,
        'show_concept': show_concept,
        'separator': separator,
        'ignore_subclass': True,  # 하위 class 무시
    }

    statements = OrderedDict()
    for tp in fs_tp:
        statements[tp] = func_fs[tp]()
        if statements[tp]:
            statements[tp] = statements[tp].to_DataFrame(**option)
    return statements


def split_columns_concept_data(columns: pd.Index) -> Tuple[Optional[pd.Index], Optional[pd.Index]]:
    regex = re.compile(r'\d{8}')

    concept_columns = []
    data_columns = []
    for column in columns:
        df_column_date = regex.findall(column[0])
        if len(df_column_date) == 0:
            concept_columns.append(column)
        else:
            data_columns.append(column)
    if len(concept_columns) > 0:
        concept_columns = pd.MultiIndex.from_tuples(concept_columns)
    else:
        concept_columns = None
    if len(data_columns) > 0:
        data_columns = pd.MultiIndex.from_tuples(data_columns)
    else:
        data_columns = None
    return concept_columns, data_columns


def sorting_data_columns(columns: pd.Index) -> pd.Index:
    def sorting(value):
        if isinstance(value, str):
            return value
        else:
            ret = [x for x in value]
            return tuple(ret)

    regex = re.compile(r'\d{8}')
    data_columns = []
    for column in columns:
        df_column_date = regex.findall(column[0])
        data_columns.append([column, df_column_date])

    data_columns.sort(key=lambda x: sorting(x[1]), reverse=True)
    data_columns = [x[0] for x in data_columns]
    data_columns = pd.MultiIndex.from_tuples(data_columns)
    return data_columns


def sorting_columns(statements: Dict[str, DataFrame]) -> Dict[str, DataFrame]:

    for tp in statements:
        df = statements[tp]
        if df is None:
            continue
        concept_columns, data_columns = split_columns_concept_data(df.columns)
        if data_columns is not None:
            data_columns = sorting_data_columns(data_columns)

        if concept_columns is not None and data_columns is not None:
            ncolumns = concept_columns.tolist() + data_columns.tolist()
            ncolumns = pd.MultiIndex.from_tuples(ncolumns)
        else:
            ncolumns = df.columns

        statements[tp] = statements[tp][ncolumns]
    return statements


def select_cumulative(corp_code, statements: Dict[str, DataFrame]) -> Dict[str, DataFrame]:
    acc_mt = get_corp_info(corp_code)['acc_mt']
    month = int(acc_mt) % 12 + 1
    start_with = '{:02}01'.format(month)
    regex_str = re.compile(r'\d{4}' + start_with)

    for tp in statements:
        if tp == 'bs':
            continue

        df = statements[tp]
        if df is None:
            continue
        concept_columns, data_columns = split_columns_concept_data(df.columns)

        if concept_columns is not None and data_columns is not None:
            data_columns = [x for x in data_columns if regex_str.search(x[0])]
            ncolumns = concept_columns.tolist() + data_columns
            ncolumns = pd.MultiIndex.from_tuples(ncolumns)
        else:
            ncolumns = df.columns

        statements[tp] = statements[tp][ncolumns]
    return statements


def drop_empty_columns(df: Dict[str, DataFrame], label_df: bool = False) -> Dict[str, DataFrame]:

    for tp in df:
        df_tp = df[tp]
        if df_tp is None:
            continue

        if label_df:
            none_columns = df_tp[df_tp != u''].isnull().all()
        else:
            none_columns = df_tp.isnull().all()

        columns = []
        for key, value in none_columns.items():
            if value is not True:
                columns.append(key)
        # convert list to numpy array
        columns = np.array(columns, dtype=object)
        df[tp] = df_tp[columns]
    return df


def remove_almost_empty_columns(df: Dict[str, DataFrame], min_data_number: int = 1) -> Dict[str, DataFrame]:
    """
    Remove almost empty columns from dataframe in dictionary.

    Args:
    df : Dict[str, DataFrame]
        The original dictionary containing dataframes.
    min_data_number : int
        The minimum number of data in a column to not be considered almost empty.

    Returns:
    df : Dict[str, DataFrame]
        The modified dictionary with almost empty columns removed.
    """

    regex = re.compile(r'\d{8}')

    for tp, df_tp in df.items():
        if df_tp is not None:
            new_columns = [col for col in df_tp.columns if (regex.search(
                col[0]) is None) or (df_tp[col].count() > min_data_number)]
            df[tp] = df_tp[new_columns]

    return df


def analyze_report(report: Report,
                   fs_tp: Tuple[str] = ('bs', 'is', 'cis', 'cf'),
                   separate: bool = False,
                   lang: str = 'ko',
                   separator: bool = True,
                   dataset: str = 'xbrl') -> Union[Dict[str, Optional[DataFrame]], None]:
    # 2012년 이후 데이터만 XBRL 데이터 추출
    year = int(report.rcept_dt[:4])
    if year > 2011 and dataset == 'xbrl':
        xbrl = report.xbrl
    else:
        xbrl = None

    # XBRL File check
    if xbrl is not None:
        if separate is False and not xbrl.exist_consolidated():
            raise NotFoundConsolidated(
                'Could not find consolidated financial statements')
        fs_df = analyze_xbrl(report, fs_tp=fs_tp, separate=separate, lang=lang,
                             show_abstract=False, show_class=True, show_depth=10,
                             show_concept=True, separator=separator)
    else:
        fs_df = _analyze_report_html(report, fs_tp=fs_tp, separate=separate, lang=lang)

    fs_df = remove_almost_empty_columns(fs_df, min_data_number=1)
    return fs_df


def _analyze_report_html(report: Report, fs_tp: Tuple[str], separate: bool, lang: str):
    fs_df = analyze_html(report, fs_tp=fs_tp, separate=separate, lang=lang)

    # If consolidated financial statements are not found, raise an NotFoundConsolidated exception
    if fs_df is None and separate is False:
        raise NotFoundConsolidated(
            'Could not find consolidated financial statements')
    return fs_df


def _analyze_xbrl_file(file_path: str, fs_tp: Tuple[str], separate: bool, lang: str, separator: bool):
    """ worker 프로세스에서 XBRL 파일을 분석 (analyze_report의 XBRL 경로와 동일, 네트워크 요청 없음)

    Returns
    -------
    tuple of (str, dict or None, list)
        ('ok' 또는 'empty', 재무제표, worker에서 발생한 warning 목록)
    """
    from types import SimpleNamespace
    import dart_fss as dart
    from dart_fss.xbrl import get_xbrl_from_file

    dart.utils.spinner.spinner_enable = False
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter('always')
        xbrl = get_xbrl_from_file(file_path)
        if xbrl.is_empty():
            fs_df, status = None, 'empty'
        else:
            if separate is False and not xbrl.exist_consolidated():
                raise NotFoundConsolidated(
                    'Could not find consolidated financial statements')
            fs_df = analyze_xbrl(SimpleNamespace(xbrl=xbrl), fs_tp=fs_tp, separate=separate, lang=lang,
                                 show_abstract=False, show_class=True, show_depth=10,
                                 show_concept=True, separator=separator)
            fs_df = remove_almost_empty_columns(fs_df, min_data_number=1)
            status = 'ok'
    return status, fs_df, [(w.category, str(w.message)) for w in caught]


class _ResultCache(object):
    """ 보고서별 재무제표 분석 결과 디스크 캐시 (extract의 cache 옵션)

    공시는 접수번호(rcept_no)별로 내용이 변경되지 않으므로 분석 결과를 저장하여 재사용한다.
    추출 옵션, dart-fss 및 pandas 버전이 다르면 다른 캐시로 취급한다.
    """
    def __init__(self, path: str):
        os.makedirs(path, exist_ok=True)
        self.path = path

    def _file(self, report: Report, kwargs: dict) -> str:
        import json
        import hashlib
        from dart_fss import __version__
        key = json.dumps({
            'rcept_no': report.rcept_no,
            'fs_tp': list(kwargs['fs_tp']),
            'separate': kwargs['separate'],
            'lang': kwargs['lang'],
            'separator': kwargs['separator'],
            'dataset': kwargs.get('dataset', 'xbrl'),
            'dart_fss': __version__,
            'pandas': pd.__version__,
        }, sort_keys=True)
        name = hashlib.sha256(key.encode('utf-8')).hexdigest()
        return os.path.join(self.path, '{}_{}.pkl'.format(report.rcept_no, name[:16]))

    def exists(self, report: Report, kwargs: dict) -> bool:
        return os.path.exists(self._file(report, kwargs))

    def load(self, report: Report, kwargs: dict):
        import pickle
        try:
            with open(self._file(report, kwargs), 'rb') as f:
                return pickle.load(f)
        except Exception:
            # 캐시가 없거나 손상된 경우 다시 분석
            return None

    def save(self, report: Report, kwargs: dict, fs_df):
        import pickle
        if fs_df is None:
            return
        file = self._file(report, kwargs)
        temp = '{}.{}.tmp'.format(file, os.getpid())
        try:
            with open(temp, 'wb') as f:
                pickle.dump(fs_df, f, protocol=pickle.HIGHEST_PROTOCOL)
            os.replace(temp, file)
        except OSError:
            if os.path.exists(temp):
                os.remove(temp)


def get_fs_cache_folder() -> str:
    """ 재무제표 분석 결과 캐시 기본 폴더 (extract의 cache=True)"""
    from dart_fss.utils import get_cache_folder
    return os.path.join(get_cache_folder(), 'fs')


def clear_fs_cache(path: str = None):
    """ 재무제표 분석 결과 캐시 삭제

    Parameters
    ----------
    path: str, optional
        캐시 폴더 (default: get_fs_cache_folder())
    """
    path = path or get_fs_cache_folder()
    if os.path.isdir(path):
        shutil.rmtree(path)


class _ParallelAnalyzer(object):
    """ 여러 보고서의 XBRL 분석을 병렬로 수행 (extract의 workers > 1)

    DART 요청 제한(IP 차단)을 피하기 위해 다운로드는 메인 프로세스에서 순차적으로 수행하고,
    XBRL 파싱 및 재무제표 생성만 별도 프로세스에서 수행한다. 결과는 보고서 순서대로 반환된다.
    XBRL 다운로드에 실패했거나 2011년 이전 보고서 등은 기존과 동일하게 analyze_report로 처리한다.
    """
    def __init__(self, workers: int, fs_tp: Tuple[str], separate: bool, lang: str, separator: bool,
                 cache: Optional[_ResultCache] = None):
        from concurrent.futures import ProcessPoolExecutor
        self.pool = ProcessPoolExecutor(max_workers=workers)
        self.cache = cache
        self.lookahead = workers * 2
        self.option = dict(fs_tp=fs_tp, separate=separate, lang=lang, separator=separator)
        self.queue = []
        self.jobs = OrderedDict()

    def schedule(self, reports: List[Report]):
        self.queue = list(reports)

    def _submit(self, report: Report):
        if int(report.rcept_dt[:4]) <= 2011:
            return None
        if self.cache is not None and self.cache.exists(report, self.option):
            return None
        path = tempfile.mkdtemp()
        try:
            file_path = download_xbrl(path=path, rcept_no=report.rcept_no)
        except Exception:
            # 실패 시 analyze_report에서 기존과 동일하게 처리(대체 경로 탐색 또는 예외 발생)
            shutil.rmtree(path, ignore_errors=True)
            return None
        return self.pool.submit(_analyze_xbrl_file, file_path, **self.option), path

    def _fill(self):
        while self.queue and len(self.jobs) < self.lookahead:
            report = self.queue.pop(0)
            self.jobs[id(report)] = self._submit(report)

    def discard(self, report: Report):
        self._fill()
        job = self.jobs.pop(id(report), None)
        self._fill()
        if job is not None:
            job[0].cancel()
            shutil.rmtree(job[1], ignore_errors=True)

    def analyze(self, report: Report, **kwargs):
        self._fill()
        job = self.jobs.pop(id(report), None)
        self._fill()
        if job is None:
            return analyze_report(report=report, **kwargs)

        future, path = job
        try:
            status, fs_df, caught = future.result()
        finally:
            shutil.rmtree(path, ignore_errors=True)
        for category, message in caught:
            warnings.warn(message, category)
        if status == 'empty':
            warnings.warn("The DART disclosure contains an XBRL file, but it is either invalid or empty.", UserWarning)
            fs_df = _analyze_report_html(report, fs_tp=self.option['fs_tp'],
                                         separate=self.option['separate'], lang=self.option['lang'])
            fs_df = remove_almost_empty_columns(fs_df, min_data_number=1)
        return fs_df

    def close(self):
        for job in self.jobs.values():
            if job is not None:
                job[0].cancel()
                shutil.rmtree(job[1], ignore_errors=True)
        self.jobs.clear()
        self.queue = []
        self.pool.shutdown(wait=True, cancel_futures=True)


def search_annual_report(corp_code: str,
                         bgn_de: str,
                         end_de: str = None,
                         separate: bool = False,
                         last_reprt_at: str = 'Y'):

    reports = []

    pblntf_detail_ty = ['A001']
    if separate:
        pblntf_detail_ty.append('F001')
    else:
        pblntf_detail_ty.append('F002')

    # finally 블록의 return은 Python 3.14부터 SyntaxWarning이므로 동일 동작으로 재작성
    # (기존과 같이 검색 중 발생한 모든 예외를 RuntimeError로 변환)
    try:
        # 사업보고서 검색(최종보고서)
        reports = search_filings(corp_code=corp_code, bgn_de=bgn_de, end_de=end_de,
                                 pblntf_detail_ty=pblntf_detail_ty, page_count=100, last_reprt_at=last_reprt_at)
    except Exception:
        raise RuntimeError('Could not find an annual report')
    if len(reports) == 0:
        raise RuntimeError('Could not find an annual report')
    return reports


# 인카금융서비스에서 반기보고서가 없는 경우 발생하는 오류 처리
def search_other_report(corp_code, bgn_de, end_de, pblntf_detail_ty):
    try:
        reports = search_filings(corp_code=corp_code, bgn_de=bgn_de, end_de=end_de,
                                 pblntf_detail_ty=pblntf_detail_ty, page_count=100, last_reprt_at='Y')
    except NoDataReceived:
        resp = {
            'page_no': 1,
            'page_count': 100,
            'total_count': 0,
            'total_page': 0,
            'list': [],
        }
        reports = SearchResults(resp)
    return reports


def extract(corp_code: str,
            bgn_de: str,
            end_de: str = None,
            fs_tp: Tuple[str] = ('bs', 'is', 'cis', 'cf'),
            separate: bool = False,
            report_tp: Union[str, List[str]] = 'annual',
            lang: str = 'ko',
            separator: bool = True,
            dataset: str = 'xbrl',
            cumulative: bool = False,
            progressbar: bool = True,
            skip_error: bool = True,
            last_report_only: bool = True,
            min_required: int = 4,
            workers: int = 1,
            cache: Union[bool, str] = False) -> FinancialStatement:
    """
    재무제표 검색

    Parameters
    ----------
    corp_code: str
        공시대상회사의 고유번호(8자리)
    bgn_de: str
        검색 시작일자(YYYYMMDD)
    end_de: str, optional
        검색 종료일자(YYYYMMDD)
    fs_tp: tuple of str, optional
        'bs' 재무상태표, 'is' 손익계산서, 'cis' 포괄손익계산서, 'cf' 현금흐름표
    separate: bool, optional
        개별재무제표 여부
    report_tp: str or list, optional
        'annual' 연간, 'half' 연간 + 반기, 'quarter' 연간 + 반기 + 분기, ['annual'] 연간, ['half'] 반기, ['quarter'] 분기, ['annual', 'half'] 연간 + 반기, ['annual', 'quarter'] 연간 + 분기, ['half', 'quarter']  반기 + 분기, ['annual', 'half', 'quarter'] 연간 + 반기 + 분기
    lang: str, optional
        'ko' 한글, 'en' 영문
    separator: bool, optional
        1000단위 구분자 표시 여부
    dataset: str, optional
        'xbrl': xbrl 파일 우선 데이터 추출, 'web': web page 우선 데이터 추출(default: 'xbrl')
    cumulative: bool, optional
        반기 혹은 분기 보고서 추출시 해당분기 값을 제외한 누적값만 추출할지 여부 (default: False)
    progressbar: bool, optional
        ProgressBar 표시 여부 (default: True)
    skip_error: bool, optional
        Error 발생시 skip 여부 (default: True)
    last_report_only: bool, optional
        최종 보고서만을 이용하여 데이터를 추출할지 여부 (default: True)
    min_required: int, optional
        Merge를 위한 최소한의 유효 데이터 개수 (default: 4)
    workers: int, optional
        XBRL 분석에 사용할 프로세스 수. 2 이상이면 다운로드는 순차적으로 하되 XBRL 분석을 병렬로 수행하며,
        결과는 동일하다. dataset='xbrl'일 때만 적용된다. Windows/macOS에서 스크립트로 실행할 경우
        ``if __name__ == '__main__':`` 블록 안에서 호출해야 한다. (default: 1)
    cache: bool or str, optional
        보고서별 분석 결과를 디스크에 저장하고 재사용할지 여부. True이면 기본 캐시 폴더
        (get_fs_cache_folder()), 문자열이면 해당 폴더를 사용한다. 캐시된 보고서는 다운로드 및 분석을
        생략하며, 분석 중 발생했던 경고는 다시 표시되지 않는다. 삭제는 clear_fs_cache() (default: False)
    Returns
    -------
    FinancialStatement
        제무제표 검색 결과

    """
    if is_notebook():
        from tqdm.notebook import tqdm
    else:
        from tqdm import tqdm

    # Disable progressbar
    tqdm_disable = not progressbar

    if dataset not in ['xbrl', 'web']:
        raise ValueError('invalid dataset type: only xbrl or web are allowed')

    all_report_tp = ('annual', 'half', 'quarter')
    all_report_name = ('Annual', 'Semiannual', 'Quarterly')
    all_pblntf_detail_ty = ('A001', 'A002', 'A003')

    if last_report_only:
        last_reprt_at = 'Y'
    else:
        last_reprt_at = 'N'

    def check_report_tp(req_tp, tp):
        if isinstance(req_tp, str):
            index = all_report_tp.index(req_tp) + 1
            if tp in all_report_tp[:index]:
                return True
            else:
                return False
        elif isinstance(req_tp, list) and tp in req_tp:
            return True
        else:
            return False

    # Spinner disable
    import dart_fss as dart
    dart.utils.spinner.spinner_enable = False
    statements = None
    label_df = None
    report = None

    regex_skip_title = str_to_regex("연장")

    result_cache = None
    if cache:
        result_cache = _ResultCache(cache if isinstance(cache, str) else get_fs_cache_folder())

    parallel = None
    if workers > 1 and dataset == 'xbrl':
        parallel = _ParallelAnalyzer(workers, fs_tp=fs_tp, separate=separate, lang=lang, separator=separator,
                                     cache=result_cache)
    analyze_func = parallel.analyze if parallel is not None else analyze_report

    def analyze(report: Report, **kwargs):
        if result_cache is None:
            return analyze_func(report=report, **kwargs)
        fs_df = result_cache.load(report, kwargs)
        if fs_df is not None:
            if parallel is not None:
                parallel.discard(report)
            return fs_df
        fs_df = analyze_func(report=report, **kwargs)
        result_cache.save(report, kwargs, fs_df)
        return fs_df

    try:
        for idx, tp in enumerate(all_report_tp):
            if check_report_tp(report_tp, tp):
                if tp == 'annual':
                    reports = search_annual_report(
                        corp_code=corp_code, bgn_de=bgn_de, end_de=end_de, separate=separate)
                else:
                    reports = search_filings(corp_code=corp_code, bgn_de=bgn_de, end_de=end_de,
                                             pblntf_detail_ty=all_pblntf_detail_ty[idx], page_count=100,
                                             last_reprt_at=last_reprt_at)

                if parallel is not None:
                    parallel.schedule([x for x in reports if not regex_skip_title.search(x.report_nm)])

                length = len(reports)
                for _ in tqdm(range(length), desc='{} reports'.format(all_report_name[idx]), unit='report', disable=tqdm_disable):
                    try:
                        report = reports.pop(0)
                        if regex_skip_title.search(report.report_nm):
                            continue

                        if statements is None:
                            statements = analyze(report=report,
                                                 fs_tp=fs_tp,
                                                        separate=separate,
                                                        lang=lang,
                                                        separator=separator)
                            if statements is None:
                                warnings_text = 'Unable to extract financial statements: {}.'.format(
                                    report.to_dict())
                                warnings.warn(warnings_text, RuntimeWarning)
                            else:
                                if separate is False and all([statements[tp] is None for tp in statements]):
                                    raise NotFoundConsolidated(
                                        'Could not find consolidated financial statements')
                                # initialize label dictionary
                                label_df = init_label(statements, fs_tp=fs_tp)
                        else:
                            nstatements = analyze(report=report,
                                                  fs_tp=fs_tp,
                                                         separate=separate,
                                                         lang=lang,
                                                         separator=separator,
                                                         dataset=dataset)
                            if nstatements is None:
                                warnings_text = 'Unable to extract financial statements: {}.'.format(
                                    report.to_dict())
                                warnings.warn(warnings_text, RuntimeWarning)
                            else:
                                statements, label_df = merge_fs(statements, nstatements,
                                                                fs_tp=fs_tp, label_df=label_df,
                                                                min_required=min_required)
                    except Exception as ex:
                        traceback.print_exc()
                        warnings_text = 'Unable to extract financial statements: {}.'.format(
                            report.to_dict())
                        if skip_error:
                            warnings.warn(warnings_text, RuntimeWarning)
                        else:
                            raise ex

        # Spinner enable
        dart.utils.spinner.spinner_enable = True
        if separate is False and (statements is None or all([statements[tp] is None for tp in statements])):
            raise NotFoundConsolidated(
                'Could not find consolidated financial statements')

        statements = drop_empty_columns(statements)
        label_df = drop_empty_columns(label_df)

        if cumulative:
            statements = select_cumulative(corp_code, statements)
            label_df = select_cumulative(corp_code, label_df)

        statements = sorting_columns(statements)
        label_df = sorting_columns(label_df)

        info = {
            'corp_code': corp_code,
            'bgn_de': bgn_de,
            'end_de': end_de,
            'separate': separate,
            'report_tp': report_tp,
            'lang': lang,
            'separator': separator
        }
        return FinancialStatement(statements, label_df, info)
    except Exception as e:
        if report is not None:
            msg = 'An error occurred while fetching or analyzing {}.'.format(
                report.to_dict())
        else:
            msg = 'Unexpected Error'
        e.args = (*e.args, msg, )
        raise e
    finally:
        dart.utils.spinner.spinner_enable = True
        if parallel is not None:
            parallel.close()

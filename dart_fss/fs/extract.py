# -*- coding: utf-8 -*-
import re
import math
import numpy as np
import pandas as pd

from typing import Union, List, Dict, Tuple, Pattern, Optional
from collections import OrderedDict
from pandas import DataFrame
from datetime import datetime
from dateutil.relativedelta import relativedelta
from bs4 import BeautifulSoup
from bs4.element import Tag

from dart_fss.filings.reports import Report
from dart_fss.filings import search as search_filings
from dart_fss.utils import str_compare, str_unit_to_number_unit, str_insert_whitespace, is_notebook
from dart_fss.errors.errors import NotFoundConsolidated, NoDataReceived
from dart_fss.utils import str_to_regex, get_currency_str
from dart_fss.fs.fs import FinancialStatement


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


def extract_date_from_header(header):
    """ 재무제표 기간 추출을 위해 사용하는 method"""
    # YYYY년 MM월 DD일 형태 검색
    regex = re.compile(r'(\d{4})[^0-9]*\s*(\d{1,2})[^0-9]*\s*(\d{1,2})')
    # YYYY년 MM월 DD일 M'M'월 D'D'일 형태 검색
    regex2 = re.compile(r'(\d{4})[^0-9]*\s*(\d{1,2})[^0-9]*\s*(\d{1,2})[^0-9]*\s*(\d{1,2})[^0-9]*\s*(\d{1,2})')
    date_info = []
    td_list = header.find_all('td')
    for td in td_list:
        # Remove white text in tag
        for tag in td.find_all(style=re.compile(r'color:#ffffff', re.IGNORECASE)):
            tag.decompose()

        searched = regex.findall(td.text)
        searched2 = regex2.findall(td.text)
        if len(searched) > 0:
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
                date.append(datetime(year, month, day))

                month = int(s[3])
                day = int(s[4])
                date.append(datetime(year, month, day))

                if len(date) > 0:
                    date_info.append(tuple(date))
            else:
                date = []
                for d in searched:
                    year = int(d[0])
                    month = int(d[1])
                    day = int(d[2])
                    date.append(datetime(year, month, day))
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
    th_colspan_list = [int(th.attrs.get('colspan', 1)) for th in thead.tr.find_all('th')]
    date_info = extract_date_from_header(fs_table['header'])
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
    columns_matrix = [[None for _y in range(col_length)] for _x in range(row_length)]
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
            date_list = [datetime(1900, 1, 1)]
            if idx == 0:
                if jdx == 0:
                    text = '과목'
                elif regex.search(text) is None:
                    if len(date_info) > 0:
                        date_list = date_info.pop(0)
                    else:
                        import warnings
                        date = '-'.join([date.strftime('%Y%m%d') for date in date_list])
                        warnings_text = "Date data length does not match table header."\
                                + "So last date was set using last data({}). ".format(date)
                        warnings.warn(warnings_text, RuntimeWarning)
                    text = '-'.join([date.strftime('%Y%m%d') for date in date_list])

            if regex.search(text):
                row_span = 2

            for mdx in range(row_span):
                for ndx in range(col_span):
                    new_text = text
                    if mdx == 0 and regex.search(text):
                        new_text = fs_string[fs_tp]
                    columns_matrix[idx + mdx][start_idx + ndx] = new_text
            start_idx = start_idx + ndx + 1

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
                date_info = [datetime.strptime(date_str, '%Y%m%d') for date_str in column[0].split('-')]

                # calculating start_dt
                delta = relativedelta(months=3)
                start_dt = date_info[1] - delta
                start_dt = start_dt.replace(day=1)

                end_dt = date_info[1]
                column[0] = '-'.join([date.strftime('%Y%m%d') for date in [start_dt, end_dt]])
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
    df = pd.DataFrame(columns=df_columns)

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

    for idx, tr in enumerate(tbody.find_all('tr')):
        extracted = [re.sub(r'\s+|=+', '', get_text_before_newline(td)) for td in tr.find_all('td')]
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

        ordered_list = []
        for column in df_columns.tolist():
            ordered_list.append(row.get(column, None))

        row_unit = unit_regex.search(ordered_list[0])
        if row_unit:
            row_unit = str_unit_to_number_unit(row_unit.group(1))
            for jdx, value in enumerate(ordered_list):
                if isinstance(value, str):
                    pass
                else:
                    ordered_list[jdx] = ordered_list[jdx] / unit * row_unit

        df.loc[idx] = ordered_list
    return df


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
                children = tag.findChildren(text=includes)
                for child in children:
                    title = child
                    if title:
                        title = re.sub(r'\s+', '', title)
                        # 만약 타이틀에 제외될 단어 포함시 Pass
                        if excludes and excludes.search(title):
                            not_headers.append(tag)
                            continue

                        # 타이틀이 너무 길때 Pass
                        if len(title) > 12:
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
        'bs': str_insert_whitespace('재무상태표') + ' OR ' + str_insert_whitespace('대차대조표'),
        'is': str_insert_whitespace('손익계산서'),
        'cis': str_insert_whitespace('포괄손익계산서'),
        'cf': str_insert_whitespace('현금흐름표'),
    }

    for key, query in queryset.items():
        if key not in fs_tp:
            continue

        # 연결재무제표 검색시 사용할 query 구문
        excludes = None
        if not separate:
            query = query + ' AND ' + str_insert_whitespace('연결')
        else:
            excludes = str_insert_whitespace('연결')

        if key == 'is':
            if excludes:
                excludes += ' OR ' + str_insert_whitespace('포괄')
            else:
                excludes = str_insert_whitespace('포괄')

        if excludes:
            excludes = str_to_regex(excludes)

        regex = str_to_regex(query)
        title, header, tb = seek_table(tables=tables, includes=regex, excludes=excludes)
        fs_table[key] = {'title': title, 'header': header, 'table': tb}
    return fs_table


def extract_fs_table(fs_table, fs_tp, separate: bool = False, lang: str = 'ko'):
    results = OrderedDict()
    for tp, table in fs_table.items():
        if tp in fs_tp:
            if table['table']:
                columns = convert_thead_into_columns(fs_tp=tp, fs_table=table, separate=separate, lang=lang)
                df = convert_tbody_to_dataframe(columns=columns, fs_table=table)
            else:
                df = None
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
            fs_table = search_fs_table(tables=tables, fs_tp=fs_tp, separate=separate)
            count = sum([fs_table[fs_tp]['table'] is not None for fs_tp in fs_table])
            if count > 0:
                searched_end = True
                break
        if searched_end:
            break
    return count, fs_table


def analyze_html(report: Report, fs_tp: Tuple[str] = ('bs', 'is', 'cis', 'cf'),
                 lang: str = 'ko', separate: bool = False) -> Dict[str, DataFrame]:
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
    query = {
        'includes': r'재무제표 OR 감사보고서',
        'excludes': r'주석 OR 결합 OR 의견 OR 수정 OR 검토보고서',
        'scope': ['attached_reports', 'pages'],
        'options': {'title': True}  # 첨부보고서 및 연결보고서의 title 까지 검색
    }

    if separate:
        query['excludes'] += ' OR 연결'
    else:
        query['includes'] += ' AND 연결'

    count, fs_table = report_find_all(report, query, fs_tp, separate)

    # 검색결과가 없을시 재검색, 검색 키워드 변경
    if count == 0:
        query = {
            'includes': r'재무제표 OR 명세서',
            'excludes': r'주석 OR 결합 OR 의견 OR 수정 OR 검토보고서',
            'scope': ['attached_reports', 'pages']
        }
        _, fs_table = report_find_all(report, query, fs_tp, separate)

    extract_results = extract_fs_table(fs_table=fs_table, fs_tp=fs_tp, separate=separate, lang=lang)
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


def compare_df_and_ndf_value(column: pd.Index,
                             df: DataFrame, ndf: DataFrame,
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

    overlap = set(df_columns).intersection(set(ndf_columns))
    nko_column = find_all_columns(ndf, r'label_ko')

    index_used = []
    for idx in range(len(df)):
        nvalue = None
        nlabel = ''
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
                w = ndf[ndf[col] == value].dropna(axis=1, how='all').dropna(how='all')
                # 만약 찾지 못하는 경우 Ref의 값의 음수와 동일한 값을 가지는 row index 찾기
                if len(w) == 0:
                    sign = -1
                    w = ndf[ndf[col] == -value].dropna(axis=1, how='all').dropna(how='all')

                found = False
                if len(w) > 0:
                    for index in w.index.values:
                        if index not in index_used:
                            nvalue = sign * ndf[column].iloc[index]
                            nlabel = ndf[nko_column].iloc[index][0]
                            nlabel = extract_account_title(nlabel)
                            index_used.append(index)
                            found = True
                            break
                if found:
                    break
        if nvalue and math.isnan(nvalue):
            nvalue = None

        ndata[idx] = nvalue
        nlabels[idx] = nlabel
    return ndata, nlabels


additional_comparison_function = [compare_df_and_ndf_label_and_concept]


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
                    label_df[tp][nlabel_columns[0]] = [extract_account_title(x) for x in list(df[concept_column[0]])]

                for column in date_columns:
                    label_df[tp][column] = list(df[ko_column])
    return label_df


def merge_fs(fs_df: Dict[str, DataFrame],
             nfs_df: Dict[str, DataFrame],
             label_df: Dict[str, DataFrame],
             fs_tp: Tuple[str] = ('bs', 'is', 'cis', 'cf')):
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
                label_df = init_label(fs_df=fs_df, fs_tp=fs_tp, label_df=label_df)

            _, df_columns = split_columns_concept_data(df.columns)
            _, ndf_columns =  split_columns_concept_data(ndf.columns)
            df_columns = set(df_columns.tolist())
            ndf_columns = set(ndf_columns.tolist())

            overlap = df_columns.intersection(ndf_columns)

            date_regex = re.compile(r'\d{8}')
            diff = [x for x in (ndf_columns - overlap) if date_regex.search(x[0])]
            diff.sort(key=lambda x: date_regex.findall(x[0])[0], reverse=True)

            # Data가 동일할 경우 Continue
            if len(diff) == 0:
                continue

            diff = pd.MultiIndex.from_tuples(diff)
            overlap = list(overlap)

            for column in diff:
                ndata = [None for _ in range(len(df))]
                nlabels = ['' for _ in range(len(df))]
                if len(overlap) > 0:
                    ndata, nlabels = compare_df_and_ndf_value(column, df, ndf, ndata, nlabels)

                for compare_func in additional_comparison_function:
                    ndata, nlabels = compare_func(column, df, ndf, label_df[tp], ndata, nlabels)

                label_df[tp][column] = nlabels
                fs_df[tp][column] = ndata

    return fs_df, label_df


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
        'separator': separator
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


def analyze_report(report: Report,
                   fs_tp: Tuple[str] = ('bs', 'is', 'cis', 'cf'),
                   separate: bool = False,
                   lang: str = 'ko',
                   separator: bool = True,
                   dataset: str = 'xbrl') -> Dict[str, Optional[DataFrame]]:
    # 2012년 이후 데이터만 XBRL 데이터 추출
    year = int(report.rcept_dt[:4])
    if year > 2011 and dataset == 'xbrl':
        xbrl = report.xbrl
    else:
        xbrl = None

    # XBRL File check
    if xbrl is not None:
        if separate is False and not xbrl.exist_consolidated():
            raise NotFoundConsolidated('Could not find consolidated financial statements')
        fs_df = analyze_xbrl(report, fs_tp=fs_tp, separate=separate, lang=lang,
                             show_abstract=False, show_class=True, show_depth=10,
                             show_concept=True, separator=separator)
    else:
        fs_df = analyze_html(report, fs_tp=fs_tp, separate=separate, lang=lang)

    return fs_df


def search_annual_report(corp_code: str,
                         bgn_de: str,
                         end_de: str = None,
                         separate: bool = False):

    reports = []
    try:
        # 사업보고서 검색(최종보고서)
        reports = search_filings(corp_code=corp_code, bgn_de=bgn_de, end_de=end_de,
                                 pblntf_detail_ty='A001', page_count=100, last_reprt_at='Y')
    except NoDataReceived:
        # 감사보고서 검색
        if separate:
            pblntf_detail_ty = 'F001'
        else:
            pblntf_detail_ty = 'F002'
        reports = search_filings(corp_code=corp_code, bgn_de=bgn_de, end_de=end_de,
                                 pblntf_detail_ty=pblntf_detail_ty, page_count=100, last_reprt_at='Y')
    finally:
        if len(reports) == 0:
            raise RuntimeError('Could not find an annual report')
        return reports


def extract(corp_code: str,
            bgn_de: str,
            end_de: str = None,
            fs_tp: Tuple[str] = ('bs', 'is', 'cis', 'cf'),
            separate: bool = False,
            report_tp: Union[str, List[str]] = 'annual',
            lang: str = 'ko',
            separator: bool = True,
            dataset: str = 'xbrl') -> FinancialStatement:
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
        str: 'annual' 연간, 'half' 연간 + 반기, 'quarter' 연간 + 반기 + 분기
        list: ['annual'] : 연간, ['half']: 반기, ['quarter'] 분기, ['annual', 'half']: 연간 + 반기
              ['annual', 'quarter']: 연간 + 분기, ['half', 'quarter']:  반기 + 분기, ['annual', 'half', 'quarter']: 연간 + 반기 + 분기
    lang: str, optional
        'ko' 한글, 'en' 영문
    separator: bool, optional
        1000단위 구분자 표시 여부
    dataset: str, optional
        'xbrl': xbrl 파일 우선 데이터 추출, 'web': web page 우선 데이터 추출(default: 'xbrl')
    Returns
    -------
    FinancialStatement
        제무제표 검색 결과

    """
    if is_notebook():
        from tqdm import tqdm_notebook as tqdm
    else:
        from tqdm import tqdm

    if dataset not in ['xbrl', 'web']:
        raise ValueError('invalid dataset type: only xbrl or web are allowed')

    all_report_tp = ('annual', 'half', 'quarter')
    all_report_name = ('Annual', 'Semiannual', 'Quarterly')
    all_pblntf_detail_ty = ('A001', 'A002', 'A003')

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
    try:
        for idx, tp in enumerate(all_report_tp):
            if check_report_tp(report_tp, tp):
                if tp == 'annual':
                    reports = search_annual_report(corp_code=corp_code, bgn_de=bgn_de, end_de=end_de, separate=separate)
                else:
                    reports = search_filings(corp_code=corp_code, bgn_de=bgn_de, end_de=end_de,
                                             pblntf_detail_ty=all_pblntf_detail_ty[idx], page_count=100, last_reprt_at='Y')
                length = len(reports)
                for _ in tqdm(range(length), desc='{} reports'.format(all_report_name[idx]), unit='report'):
                    report = reports.pop(0)
                    if statements is None:
                        statements = analyze_report(report=report,
                                                    fs_tp=fs_tp,
                                                    separate=separate,
                                                    lang=lang,
                                                    separator=separator)
                        if separate is False and all([statements[tp] is None for tp in statements]):
                            raise NotFoundConsolidated('Could not find consolidated financial statements')
                        # initialize label dictionary
                        label_df = init_label(statements, fs_tp=fs_tp)

                    else:
                        nstatements = analyze_report(report=report,
                                                     fs_tp=fs_tp,
                                                     separate=separate,
                                                     lang=lang,
                                                     separator=separator,
                                                     dataset=dataset)
                        statements, label_df = merge_fs(statements, nstatements, fs_tp=fs_tp, label_df=label_df)

        statements = drop_empty_columns(statements)
        label_df = drop_empty_columns(label_df)

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
        # Spinner enable
        dart.utils.spinner.spinner_enable = True
        return FinancialStatement(statements, label_df, info)
    except Exception as e:
        if report is not None:
            msg = 'An error occurred while fetching or analyzing {}.'.format(report.to_dict())
        else:
            msg = 'Unexpected Error'
        e.args = (*e.args, msg, )
        raise e
    finally:
        dart.utils.spinner.spinner_enable = True

# -*- coding: utf-8 -*-
import re
import math
import copy
import pandas as pd

from typing import Union, List, Dict, Tuple, Pattern
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
from dart_fss.utils.regex import str_to_regex
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
    str_unit = str_to_regex('원 OR USD').search(str_unit)
    if str_unit:
        str_unit = str_unit.group(0)
        str_unit = 'KRW' if str_compare('원', str_unit) else 'USD'
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
    columns_matrix = [[None for y in range(col_length)] for x in range(row_length)]
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

    for idx, tr in enumerate(tbody.find_all('tr')):
        extracted = [re.sub(r'\s+|=+', '', td.text) for td in tr.find_all('td')]
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
    regex = re.compile(r'\d{4}(.*?)\d{2}(.*?)\d{2}')
    for table in tables:
        for tag in table.previous_siblings:
            if tag in tables:
                break
            if isinstance(tag, Tag):
                children = tag.findChildren(text=includes)
                for child in children:
                    title = child
                    if title:
                        title = re.sub(r'\s+', '', title)
                        if excludes and excludes.search(title):
                            continue
                        if len(title) > 12:
                            continue
                        header = table.find_previous('table', class_='nb')
                        if header is None:
                            continue
                        tr_list = header.find_all('tr')
                        if len(tr_list) < 2:
                            continue

                        tr_cnt = 0
                        for tr in tr_list:
                            if regex.search(tr.text):
                                tr_cnt += 1

                        if tr_cnt == 0:
                            found = table.find_previous(text=re.compile(r'\d{4}(.*?)\d{2}(.*?)\d{2}'))
                            if found is None:
                                continue
                            header = found.parent
                            extract_text = re.sub('<.*?>', '\n', str(header))
                            extract_text = extract_text.split('\n')
                            html = '<table class="nb"><tbody>'

                            error = False
                            for t in extract_text:
                                if t.strip() == '':
                                    pass
                                else:
                                    if len(t) > 100:
                                        error = True
                                        break
                                    html += '<tr><td>' + t + '</td></tr>'
                            if error:
                                continue
                            html += '</tbody></table>'
                            header = BeautifulSoup(html, 'html.parser')
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
        'excludes': r'주석 OR 결합 OR 의견 OR 수정',
        'scope': ['attached_reports', 'pages'],
        'options': {'title': True} # 첨부보고서 및 연결보고서의 title 까지 검색
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
            'excludes': r'주석 OR 결합 OR 의견 OR 수정',
            'scope': ['attached_reports', 'pages']
        }
        _, fs_table = report_find_all(report, query, fs_tp, separate)

    extract_results = extract_fs_table(fs_table=fs_table, fs_tp=fs_tp, separate=separate, lang=lang)
    return extract_results


def find_all_columns(df: DataFrame, query: str) -> list:
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
    return results


def extract_account_title(title):
    title = title.split('.')
    if len(title) == 1:
        title = title[0]
    elif len(title) > 1:
        title = ''.join(title[1:])
    title = re.sub(r'\[.*?\]|\(.*?\)|<.*?>', '', title)
    title = re.sub(r'\s+', '', title)
    return title


def compare_df_and_ndf_label(column: Tuple[Union[str, Tuple[str]]],
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

    for idx, value in enumerate(ndata):
        if isinstance(value, str):
            pass
        elif value is None:
            pass
        elif math.isnan(value):
            pass
        else:
            continue

        label = df[df_label_column].iloc[idx]
        label = re.sub(r'\s+', '', label)
        label = extract_account_title(label)
        label_set = set(ldf.iloc[idx])
        label_set.add(label)
        label_none_data.append((idx, label_set))

    matched = []
    used = []
    for idx in range(len(ndf)):
        if idx in matched:
            continue
        label = extract_account_title(ndf[ndf_label_column].iloc[idx])

        for index, label_set in label_none_data:
            if index in used:
                continue
            if label in label_set:
                value = ndf[column].iloc[idx]
                if isinstance(value, str):
                    pass
                else:
                    used.append(index)
                    matched.append(idx)
                    ndata[index] = value
                    nlabels[index] = label

    return ndata, nlabels


def compare_df_and_ndf_value(column: Tuple[Union[str, Tuple[str]]],
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
    df_columns = set(df.columns.tolist())
    ndf_columns = set(ndf.columns.tolist())
    overlap = df_columns.intersection(ndf_columns)

    nko_column = find_all_columns(ndf, r'label_ko')

    index_used = []
    for idx in range(len(df)):
        for col in overlap:
            nvalue = None
            nlabel = ''
            value = df[col].iloc[idx]
            if isinstance(value, str):
                pass
            elif value is None:
                pass
            elif value and math.isnan(value):
                pass
            else:
                w = ndf[ndf[col] == value].dropna(axis=1, how='all').dropna(how='all')
                if len(w) > 0:
                    for index in w.index.values:
                        if index not in index_used:
                            nvalue = ndf[column].iloc[index]
                            nlabel = ndf[nko_column].iloc[index][0]
                            nlabel = extract_account_title(nlabel)
                            index_used.append(index)
                            break
        if nvalue and math.isnan(nvalue):
            nvalue = None

        ndata[idx] = nvalue
        nlabels[idx] = nlabel
    return ndata, nlabels


additional_comparison_function = [compare_df_and_ndf_label]


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
                    label_df[tp][label_columns[0]] = [extract_account_title(x) for x in list(df[concept_column[0]])]

                for column in date_columns:
                    label_df[tp][column] = list(df[ko_column])
    return label_df


def merge_fs(fs_df: Dict[str, DataFrame], label_df: Dict[str, DataFrame],
             report: Report, fs_tp: Tuple[str] = ('bs', 'is', 'cis', 'cf'),
             lang: str = 'ko', separate: bool = False):
    """
    재무제표 DataFrame과 Report의 데이터를 합쳐주는 Method

    Parameters
    ----------
    fs_df: dict of {str: DataFrame}
        재무제표
    label_df: dict of {str: DataFrame}
        재무제표 검색결과시 추출된 값의 Label
    report: Report
        Report
    fs_tp: tuple of str, optional
        'bs' 재무상태표, 'is' 손익계산서, 'cis' 포괄손익계산서, 'cf' 현금흐름표
    lang: str, optional
        'ko' 한글, 'en' 영문
    separate: bool, optional
        개별재무제표 여부

    Returns
    -------
    tuple of dict of {str: DataFrame}
        재무제표, 추출된 Label 리스트
    """
    try:
        global additional_comparison_function
        # 보고서의 웹페이지에서 재무제표 추출
        nfs_df = analyze_html(report=report, fs_tp=fs_tp, lang=lang, separate=separate)

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

                df_columns = set(df.columns.tolist())
                ndf_columns = set(ndf.columns.tolist())

                overlap = df_columns.intersection(ndf_columns)

                date_regex = re.compile(r'\d{8}')
                diff = [x for x in (ndf_columns - overlap) if date_regex.search(x[0])]
                diff.sort(key=lambda x: date_regex.findall(x[0])[0], reverse=True)

                # Data가 동일할 경우 Continue
                if len(diff) == 0:
                    continue

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
    except Exception:
        msg = 'An error occurred while fetching or analyzing {}.'.format(report.to_dict())
        raise RuntimeError(msg)


def analyze_xbrl(report, fs_tp: Tuple[str] = ('bs', 'is', 'cis', 'cf'), separate: bool = False, lang: str = 'ko',
                 show_abstract: bool = False, show_class: bool = True, show_depth: int = 10,
                 show_concept: bool = True, separator: bool = True) -> Dict[str, DataFrame]:
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
    dict of {str : DataFrame}
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


def sorting_columns(statements: Dict[str, DataFrame]) -> Dict[str, DataFrame]:
    regex = re.compile(r'\d{8}')

    def sorting(value):
        if isinstance(value, str):
            return value
        else:
            ret = [x for x in value]
            return tuple(ret)

    for tp in statements:
        df = statements[tp]
        if df is None:
            continue

        columns = df.columns
        concept_columns = []
        date_columns = []
        for column in columns:
            df_column_date = regex.findall(column[0])
            if len(df_column_date) == 0:
                concept_columns.append(column)
            else:
                date_columns.append([column, df_column_date])

        date_columns.sort(key=lambda x: sorting(x[1]), reverse=True)
        date_columns = [x[0] for x in date_columns]

        ncolumns = concept_columns + date_columns
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

        df[tp] = df_tp[columns]
    return df


def extract(corp_code: str,
            bgn_de: str,
            end_de: str = None,
            fs_tp: Tuple[str] = ('bs', 'is', 'cis', 'cf'),
            separate: bool = False,
            report_tp: str = 'annual',
            lang: str = 'ko',
            separator: bool = True) -> FinancialStatement:
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
    report_tp: str, optional
        'annual' 1년, 'half' 반기, 'quarter' 분기
    lang: str, optional
        'ko' 한글, 'en' 영문
    separator: bool, optional
        1000단위 구분자 표시 여부

    Returns
    -------
    FinancialStatement
        제무제표 검색 결과

    """
    if is_notebook():
        from tqdm import tqdm_notebook as tqdm
    else:
        from tqdm import tqdm

    # 재무제표 검색 결과
    statements = None
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

        next_index = 0
        for idx, _ in enumerate(reports):
            # 가장 최근 보고서의 경우 XBRL 파일을 이용하여 재무제표 검색
            latest_report = reports[idx]
            latest_xbrl = latest_report.xbrl
            # XBRL 파일이 존재할 때
            if latest_xbrl is not None:
                if separate is False and not latest_xbrl.exist_consolidated():
                    raise NotFoundConsolidated('Could not find consolidated financial statements')

                # XBRL 정보를 이용하여 재무제표 정보 초기화
                analyzed_results = analyze_xbrl(latest_report, fs_tp=fs_tp, separate=separate, lang=lang,
                                                show_abstract=False, show_class=True,
                                                show_depth=10, show_concept=True, separator=separator)
                statements = copy.deepcopy(analyzed_results)
            else:
                statements = analyze_html(latest_report, fs_tp=fs_tp, separate=separate, lang=lang)
            # Report 에 재무제표 정보 없이 수정 사항만 기록된 경우 다음 리포트 검색
            if statements is not None:
                next_index = idx + 1
                break

        if separate is False and all([statements[tp] is None for tp in statements]):
            raise NotFoundConsolidated('Could not find consolidated financial statements')

        # initialize label dictionary
        label_df = init_label(statements, fs_tp=fs_tp)

        for report in tqdm(reports[next_index:], desc='Annual reports', unit='report'):
            statements, label_df = merge_fs(statements, label_df, report, fs_tp=fs_tp, separate=separate, lang=lang)

        if str_compare(report_tp, 'half') or str_compare(report_tp, 'quarter'):
            half = search_filings(corp_code=corp_code, bgn_de=bgn_de, end_de=end_de,
                                  pblntf_detail_ty='A002', page_count=100, last_reprt_at='Y')
            for report in tqdm(half, desc='Semiannual reports', unit='report'):
                statements, label_df = merge_fs(statements, label_df, report, fs_tp=fs_tp, separate=separate, lang=lang)

        if str_compare(report_tp, 'quarter'):
            quarter = search_filings(corp_code=corp_code, bgn_de=bgn_de, end_de=end_de,
                                     pblntf_detail_ty='A003', page_count=100, last_reprt_at='Y')
            for report in tqdm(quarter, desc='Quarterly report', unit='report'):
                statements, label_df = merge_fs(statements, label_df, report, fs_tp=fs_tp, separate=separate, lang=lang)

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
        return FinancialStatement(statements, label_df, info)

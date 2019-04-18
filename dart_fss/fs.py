# -*- coding: utf-8 -*-
import re
import pandas as pd

from typing import List, Dict

from pandas import DataFrame
from datetime import datetime
from tqdm import tqdm
from bs4 import BeautifulSoup

from .reports import Report
from .search import search_report_with_cache
from ._utils import compare_str, korean_unit_to_number_unit


def rename_columns(header: Dict[str, Dict[str, str]], columns: List[str],
                   lang: str = 'ko', separate: bool = False) -> List[str]:
    """ DataFrame 의 columns 이름을 html 을 참고하여 변환

    Parameters
    ----------
    header: dict of dict
        html 에서 추출한 값
    columns: list of str
        DataFrame 의 columns 이름
    lang: str, optional
        'ko' 한글, 'en' 영
    separate: bool
        개별 제무제표 유무

    Returns
    -------
    list of str
        columns 이름들
    """
    regex = re.compile(r'(제.*분?기초?)')
    regex_3month = re.compile(r'3개월')
    new_col = []

    for col_name in columns:
        new_col_name = col_name
        if regex.search(col_name):
            key = regex.search(col_name).group(1).replace(' ', '')
            if separate:
                title = '별도재무제표' if compare_str(lang, 'ko') else 'Separate'
            else:
                title = '연결재무제표' if compare_str(lang, 'ko') else 'Consolidated'
            if regex_3month.search(col_name):
                additional = '(3M)'
            else:
                additional = ''

            if header[key]['instant_datetime'] is None:
                start_datetime = header[key]['start_datetime'].strftime('%Y-%m-%d')
                end_datetime = header[key]['end_datetime'].strftime('%Y-%m-%d')
                new_col_name = '[{},{}]{}{}'.format(start_datetime, end_datetime, title, additional)
            else:
                instant_datetime = header[key]['instant_datetime'].strftime('%Y-%m-%d')
                new_col_name = '[{}]{}{}'.format(instant_datetime, title, additional)
        new_col.append(new_col_name)
    return new_col


def str_to_float(text: str) -> float:
    """ 문자를 float 데이터로 변환

    문자를 float 데이터로 변환, (1,000) 같은 경우 -1000 으로 변환

    Parameters
    ----------
    text: str
        입력문자

    Returns
    -------
    float
        변환된 숫자
    """
    regex = re.compile(r'\((.*?)\)')
    if isinstance(text, str):
        try:
            text = text.replace(',', '')
            if regex.search(text):
                value = regex.search(text).group(1)
                return -float(value)
            else:
                return float(text)
        except ValueError:
            return float('nan')

    elif isinstance(text, (int, float)):
        return float(text)
    else:
        raise ValueError('Invalid Value: {}'.format(text))


def get_table_header(soup: BeautifulSoup) -> List[str]:
    """ Table 의 Header 를 반환하는 함수

    Parameters
    ----------
    soup: BeautifulSoup
        Table의 BeautifulSoup Object

    Returns
    -------
    list of str
        Table Header
    """
    thead = soup.findChild('thead')
    if thead:
        thead_row = thead.findAll('tr')
        tags = 'th'
    else:
        thead = soup.findChild('tbody')
        thead_row = thead.findAll('tr')
        first_row = thead_row[0]
        max_row_span = 1
        for col in first_row.findAll('td'):
            row_span = int(col.attrs.get('rowspan', 1))
            if row_span > max_row_span:
                max_row_span = row_span
        thead_row = thead_row[0:max_row_span]
        tags = 'td'

    columns_name = []
    is_empty = []

    for idx, row in enumerate(thead_row):
        for col in row.findAll(tags):
            row_span = int(col.attrs.get('rowspan', 1))
            col_span = int(col.attrs.get('colspan', 1))

            if idx == 0:
                for _ in range(col_span):
                    columns_name.append(col.text)
                    if 1 < row_span:
                        is_empty.append(False)
                    else:
                        is_empty.append(True)
            else:
                start_index = 0
                for jdx, _ in enumerate(is_empty):
                    if is_empty[jdx] is True:
                        start_index = jdx
                        break

                for jdx in range(start_index, start_index+col_span):
                    columns_name[jdx] += col.text
                    is_empty[jdx] = False

    columns_name = [col.replace('\n', ' ') for col in columns_name]
    return columns_name


def get_table_body(soup: BeautifulSoup) -> str:
    """ table 의 body 부분만 str 로 반환하는 함수"""
    tbody = soup.findChild('tbody')
    return '<table>' + str(tbody) + '</table>'


def html_to_df(soup: BeautifulSoup, regex_text: str, separate=False, lang='ko') -> DataFrame:
    """ html 에서 DataFrame 추출

    Parameters
    ----------
    soup: BeautifulSoup
        Html 의 BeautifulSoup
    regex_text: str
        추출할 Table 이름의 regular expression
    separate: bool, optional
        개별 제무제표 유무
    lang: str, optional
        'ko' 한글, 'en' 영어

    Returns
    -------
    DataFrame
        추출한 Table 의 DataFrame
    """
    element = soup.find(text=re.compile(regex_text))
    if element is None:
        return None

    header_html = element.findParent('table', {'class': 'nb'})
    if header_html is None:
        header_html = element.findNext('table', {'class': 'nb'})

    won_regex = re.compile(r'(\w{0,3}원)')
    korean_unit = header_html.find(text=won_regex)
    if korean_unit is None:
        korean_unit = header_html.findNext(text=won_regex)

    unit = korean_unit_to_number_unit(str(korean_unit))

    def stod(year, month, day): return datetime(year=int(year), month=int(month), day=int(day))

    extract_header = re.findall(r'(제.*분?기초?).*(\d{4})[^0-9]*\s*(\d{1,2})[^0-9]*\s*(\d{1,2}).*현재',
                                header_html.text)
    if len(extract_header) > 0:
        header = {key.replace(' ', ''): {'instant_datetime': stod(iye, imo, ida),
                                         'start_datetime': None,
                                         'end_datetime': None}
                  for key, iye, imo, ida in extract_header}
    else:
        reg_text = r'(제.*분?기초?).*(\d{4})[^0-9]*\s*(\d{1,2})[^0-9]*\s*(\d{1,2})'
        reg_text += r'.*(\d{4})[^0-9]*\s*(\d{1,2})[^0-9]*\s*(\d{1,2})'
        extract_header = re.findall(reg_text, header_html.text)
        header = {key.replace(' ', ''): {'instant_datetime': None,
                                         'start_datetime': stod(sy, sm, sd),
                                         'end_datetime': stod(ey, em, ed)}
                  for key, sy, sm, sd, ey, em, ed in extract_header}
    table_html = header_html.findNext('table', {'class': ''})

    columns = get_table_header(table_html)
    tbody = get_table_body(table_html)
    df = pd.read_html(tbody)[0]
    df.columns = rename_columns(header=header, columns=columns, lang=lang, separate=separate)
    for column in df.columns[1:]:
        df[column] = df[column].apply(str_to_float)

    df[df.columns[1:]] = df[df.columns[1:]].apply(lambda x: x * unit)

    df.columns = ['label_ko'] + list(df.columns[1:])
    return df


def get_regex(parsing_table: List[str]):
    """추출할 table 검색을 위한 regular expression"""

    regex = r'\s*'.join(parsing_table[0])
    for table in parsing_table[1:]:
        regex += r'|' + r'\s*'.join(table)
    return regex


def read_fs_table(report: Report, fs_tp: str = 'fs',
                  lang: str = 'ko', separate: bool = False) -> DataFrame:
    """ Report 에서 DataFrame 추출

    Parameters
    ----------
    report: Report
        추출할 리포트
    fs_tp: str, optional
        'fs' 재무상태표, 'is' 손익계산서, 'ci' 포괄손익계산서, 'cf' 현금흐름표
    lang: str, optional
        'ko' 한글, 'en' 영문
    separate: bool, optional
        개별 제무제표 유무

    Returns
    -------
    DataFrame
        html 에서 추출한 DataFrame
    """
    options = {
        'includes': '재무제표',
        'excludes': ['주석', '연결'] if separate else '주석',
        'progressbar_disable': True
    }
    page = report.load_page(**options)
    if len(page) == 0:
        return None
    else:
        page = page[0]
    soup = BeautifulSoup(page.html, 'html.parser')
    if fs_tp == 'fs':
        separate_table = ['^재무상태표$', '^대차대조표$']
        consolidated_table = ['연결재무상태표', '연결대차대조표']
    elif fs_tp == 'is':
        separate_table = ['^손익계산서$']
        consolidated_table = ['연결 손익계산서']
    elif fs_tp == 'ci':
        separate_table = ['^포괄손익계산서']
        consolidated_table = ['연결 포괄손익계산서']
    elif fs_tp == 'cf':
        separate_table = ['^현금흐름표$']
        consolidated_table = ['연결 현금흐름표']
    else:
        raise ValueError('Invalid fs_tp')
    separate_table = get_regex(separate_table)
    consolidated_table = get_regex(consolidated_table)

    regex_text = separate_table if separate else consolidated_table

    df = html_to_df(soup, regex_text, separate=separate, lang=lang)
    return df


list_of_report = List[Report]


def append_fs(financial_statements: DataFrame, reports: list_of_report,
              fs_tp: str = 'fs', separate=False, lang='ko', report_tp='annual') -> DataFrame:
    """ 제무제표 DataFrame 에 데이터 추가

    Parameters
    ----------
    financial_statements: DataFrame
        제무제표 DataFrame
    reports: list of Report
        추가할 Report 리스트
    fs_tp: str, optional
        'fs' 재무상태표, 'is' 손익계산서, 'ci' 포괄손익계산서, 'cf' 현금흐름표
    separate: bool, optional
        개별 제무제표 유무
    lang: str, optional
        'ko' 한글, 'en' 영문

    Returns
    -------
    DataFrame
        제무제표 DataFrame
    """
    desc = 'Loading report - {}'.format(report_tp)
    regex_label = re.compile(r'[ㄱ-힣]+\(?[ㄱ-힣]+\)?')
    for report in tqdm(reports[1:], desc=desc, unit='page'):
        fs = read_fs_table(report, fs_tp=fs_tp, separate=separate, lang=lang)

        if fs is None:
            continue

        overlap = set(fs.columns[1:]).intersection(set(financial_statements.columns))
        if len(overlap) == 0:
            continue

        non_overlap = list(set(fs.columns[1:]) - overlap)
        overlap = list(overlap)

        refs = [tuple(financial_statements[overlap].iloc[idx]) for idx in range(len(financial_statements))]
        if 'label_ko' in financial_statements.columns:
            refs_label = [financial_statements['label_ko'].iloc[idx].replace(' ', '')
                          for idx in range(len(financial_statements))]
        else:
            refs_label = []

        data_set = dict()
        data_set_label = dict()
        for idx in range(len(fs)):
            keys = tuple(fs[overlap].iloc[idx])
            is_nan = True
            for key in keys:
                if key != float('nan'):
                    is_nan = False
                    break
            if is_nan is True:
                break
            data = fs.iloc[idx].to_dict()
            data_set[keys] = data
            label = fs['label_ko'].iloc[idx]
            if isinstance(label, str):
                label = label.replace(' ', '')
                label = regex_label.search(label).group(0)
                data_set_label[label] = data

        column_data = {column: [] for column in non_overlap}

        for ref_val, ref_label in zip(refs, refs_label):
            value = data_set.get(ref_val, data_set_label.get(ref_label, None))
            for column in non_overlap:
                data = None
                if value is not None:
                    data = value[column]
                column_data[column].append(data)

        for column in non_overlap:
            financial_statements[column] = column_data[column]

    return financial_statements


def get_statement_dataframe(xbrl, fs_tp='fs', separate: bool = False, lang: str = 'ko',
                            show_abstract: bool = False, show_class: bool = True, show_depth: int = 10,
                            show_concept: bool = True, separator: bool = True):
    if compare_str(fs_tp, 'fs'):
        statements = xbrl.get_financial_statement(separate=separate)
    elif compare_str(fs_tp, 'is'):
        statements = xbrl.get_income_statement(separate=separate)
    elif compare_str(fs_tp, 'ci'):
        statements = xbrl.get_income_statement(separate=separate)
    elif compare_str(fs_tp, 'cf'):
        statements = xbrl.get_cash_flows(separate=separate)
    else:
        raise ValueError('Invalid fs_tp')

    # 개별 기업 제무제표만 있을 때 처리
    if statements:
        if compare_str(fs_tp, 'ci') and len(statements) > 1:
            statements = statements[1]
        else:
            statements = statements[0]
    else:
        return None

    option = {
        'title': 'Separate' if separate else 'Consolidated',
        'lang': lang,
        'show_abstract': show_abstract,
        'show_class': show_class,
        'show_depth': show_depth,
        'show_concept': show_concept,
        'separator': separator
    }
    return statements.to_Dataframe(**option)


def search_financial_statement(crp_cd: str, start_dt: str, end_dt: str = None, fs_tp: str = 'fs',
                               separate: bool = False, report_tp: str = 'annual', lang: str = 'ko',
                               show_abstract: bool = False, show_class: bool = True, show_depth: int = 10,
                               show_concept: bool = True, separator: bool = True) -> DataFrame:
    """ 재무제표 검색

    Parameters
    ----------
    crp_cd: str
        종목코드
    start_dt: str
        검색 시작일자(YYYYMMDD)
    end_dt: str, optional
        검색 종료일자(YYYYMMDD)
    fs_tp: str, optional
        'fs' 재무상태표, 'is' 손익계산서, 'ci' 포괄손익계산서, 'cf' 현금흐름표
    separate: bool, optional
        개별지업 여뷰
    report_tp: str, optional
        'annual' 1년, 'half' 반기, 'quarter' 분기
    lang: str, optional
        'ko' 한글, 'en' 영문
    show_abstract: bool, optional
        abstract 표기 여부
    show_class: bool, optional
        class 표기 여부
    show_depth: int, optional
        class 표시 깊이
    show_concept: bool, optional
        concept 표시 여부
    separator: bool, optional
        1000단위 구분자 표시 여부

    Returns
    -------
    DataFrame or None
        제무제표 검색 결과

    """
    statements = None
    reports = search_report_with_cache(crp_cd=crp_cd, start_dt=start_dt, end_dt=end_dt, bsn_tp='A001', page_set=100)
    if len(reports) == 0:
        raise FileNotFoundError('Could not find an annual report')
    for idx, _ in enumerate(reports):
        last_report = reports[idx]
        last_xbrl = last_report.xbrl

        if last_xbrl is not None:
            statements = get_statement_dataframe(last_xbrl, fs_tp=fs_tp, separate=separate, lang=lang,
                                                 show_abstract=show_abstract, show_class=show_class,
                                                 show_depth=show_depth, show_concept=show_concept, separator=separator)
        else:
            statements = read_fs_table(last_report, fs_tp=fs_tp, separate=separate, lang=lang)

        # Report 에 재무제표 정보 없이 수정 사항만 기록된 경우 다음 리포트 검색
        if statements is not None:
            break

    statements = append_fs(statements, reports, fs_tp=fs_tp, separate=separate, lang=lang)

    if compare_str(report_tp, 'half') or compare_str(report_tp, 'quarter'):
        half = search_report_with_cache(crp_cd=crp_cd, start_dt=start_dt, end_dt=end_dt,
                                        bsn_tp=['A002'], page_set=100, series='asc')
        statements = append_fs(statements, half, fs_tp=fs_tp, separate=separate, lang=lang, report_tp='half')

    if compare_str(report_tp, 'quarter'):
        quarter = search_report_with_cache(crp_cd=crp_cd, start_dt=start_dt, end_dt=end_dt,
                                           bsn_tp=['A003'], page_set=100, series='asc')
        statements = append_fs(statements, quarter, fs_tp=fs_tp, separate=separate, lang=lang, report_tp='quarter')

    columns = list(statements.columns)
    data_columns = []
    label_columns = []
    regex_square = re.compile(r'\[(.*)\]')
    for col in columns:
        if regex_square.search(col):
            data_columns.append(col)
        else:
            label_columns.append(col)

    data_columns.sort(reverse=True)
    ordered_columns = label_columns + data_columns
    return statements[ordered_columns]


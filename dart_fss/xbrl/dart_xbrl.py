# -*- coding: utf-8 -*-
import re
import pandas as pd
from typing import List, Union

from pandas import DataFrame
from arelle import ModelXbrl, XbrlConst

from dart_fss.utils import str_compare, dict_to_html
from dart_fss.xbrl.table import Table
from dart_fss.xbrl.helper import (get_title, consolidated_code_to_role_number,
                                  get_statement_role_numbers)


DATASET_TITLE = {
    'dart-gcd_StatementOfFinancialPosition': '재무상태표',
    'dart-gcd_StatementOfComprehensiveIncome': '손익계산서',
    'dart-gcd_StatementOfChangesInEquity': '자본변동표',
    'dart-gcd_StatementOfCashFlows': '현금흐름표',
}


class DartXbrl(object):
    """ XBRL 문서

    회사(종목)의 XBRL 문서를 기반으로 회계정보를 가지고 있는 클래스

    Attributes
    ----------
    filename: str
        로드한 파일 이름
    xbrl: ModelXbrl
        arelle Xbrl 클래스

    """
    def __init__(self, filename: str, xbrl: ModelXbrl):
        self.filename = filename
        self.xbrl = xbrl
        self._tables = None
        self._link_roles = None

    def is_empty(self) -> bool:
        if not self.tables:
            return True

        data = [
            self.get_financial_statement(False),
            self.get_financial_statement(True),
            self.get_income_statement(False),
            self.get_income_statement(True),
            self.get_changes_in_equity(False),
            self.get_changes_in_equity(True),
            self.get_cash_flows(False),
            self.get_cash_flows(True),
        ]
        return all(x is None for x in data)

    @property
    def tables(self) -> List[Table]:
        """list of Table: Table 리스트"""
        if self._tables is not None:
            return self._tables

        arcrole = XbrlConst.parentChild
        relationship = self.xbrl.relationshipSet(arcrole)

        tables = None
        if relationship is not None:
            tables = []
            for uri in relationship.linkRoleUris:
                role_types = self.xbrl.roleTypes.get(uri)

                if role_types is not None:
                    definition = (role_types[0].genLabel(lang='ko', strip=True)
                                  or role_types[0].definition or uri)
                else:
                    definition = uri

                role_code = re.search(r"\[(.*?)\]", definition)
                role_code = role_code.group(1) if role_code else None
                tables.append(Table(self, self.xbrl, role_code, definition, uri))

        def extract_role_number(role: str):
            try:
                return int(re.search(r'(\d+)', role).group(1))
            except AttributeError:
                return 987654321

        tables.sort(key=lambda x: int(extract_role_number(x.code)))
        self._tables = tables
        return tables

    def get_table_by_code(self, code: str) -> Union[Table, None]:
        """ Table 코드와 일치하는 Table 반환

        Parameters
        ----------
        code: str
            Table 코드번호

        Returns
        -------
        Table or None
            코드 번호에 맞는 Table 또는 None
        """
        for table in self.tables:
            if str_compare(table.code, code):
                return table
        return None

    def get_table_by_name(self, name: str, separate:bool = False) -> Union[List[Table], None]:
        """ Table 이름과 일치하는 Table 리스트 반환

        Parameters
        ----------
        name: str
            Table 이름
        separate: bool, optional
            True: 개별재무제표

        Returns
        -------
        List[Table] or None
            이름에 맞는 Table 리스트 또는 None
        """

        regex = re.compile(name, re.IGNORECASE)
        regex2 = re.compile("consolidated" if not separate else "separate", re.IGNORECASE)

        tables = []
        for table in self.tables:
            if re.search(regex, table.definition) and re.search(regex2, table.definition):
                tables.append(table)
        return tables if len(tables) > 0 else None

    def _to_info_DataFrame(self, code: str, lang: str = 'ko') -> Union[DataFrame, None]:
        """ to_DataFrame wrapper

        Parameters
        ----------
        code: str
            Table Code
        lang: str
            'ko' or 'en'

        Returns
        -------
        DataFrame or None
            Pandas DataFrame
        """
        table = self.get_table_by_code(code)
        if table is None:
            return None
        return table.to_DataFrame(lang=lang, show_class=False, show_concept=False, separator=False, ignore_subclass=False)

    def get_document_information(self, lang: str = 'ko') -> Union[DataFrame,None]:
        """ 공시 문서 정보

        Parameters
        ----------
        lang: str
            표시 언어 설정('ko': 한글, 'en': 영어)

        Returns
        -------
        DataFrame or None
            공시 문서 정보
        """
        return self._to_info_DataFrame('d999001', lang=lang)

    def get_period_information(self, lang: str = 'ko') -> Union[DataFrame, None]:
        """ 공시 문서 기간 정보

        Parameters
        ----------
        lang: str
            표시 언어 설정('ko': 한글, 'en': 영어)

        Returns
        -------
        DataFrame or None
            공시 문서 기간 정보
        """
        df = self._to_info_DataFrame('d999002', lang=lang)
        if df is None:
            return None
        data = df[df.columns[2:]].iloc[3]
        data_set = [(key, data[key]) for key in data.keys()]
        new_columns = list(df.columns[:2]) + [data[0] for data in sorted(data_set, key=lambda x: x[1], reverse=True)]
        new_columns = pd.MultiIndex.from_tuples(new_columns)
        return df[new_columns]

    def get_audit_information(self, lang: str = 'ko') -> Union[DataFrame, None]:
        """ 감사 정보

        Parameters
        ----------
        lang: str
            표시 언어 설정('ko': 한글, 'en': 영어)

        Returns
        -------
        DataFrame or None
            감사 정보
        """
        return self._to_info_DataFrame('d999003', lang=lang)

    def get_entity_information(self, lang: str = 'ko') -> Union[DataFrame, None]:
        """ 공시 대상 정보

        Parameters
        ----------
        lang: str
            표시 언어 설정('ko': 한글, 'en': 영어)

        Returns
        -------
        DataFrame or None
            공시 대상 정보
        """
        return self._to_info_DataFrame('d999004', lang=lang)

    def get_entity_address_information(self, lang: str = 'ko') -> Union[DataFrame, None]:
        """ 주소 정보

        Parameters
        ----------
        lang: str
            표시 언어 설정('ko': 한글, 'en': 영어)

        Returns
        -------
        DataFrame or None
            주소 정보

        """
        return self._to_info_DataFrame('d999005', lang=lang)

    def get_author_information(self, lang: str = 'ko') -> Union[DataFrame, None]:
        """ 작성자 정보

        Parameters
        ----------
        lang: str
            표시 언어 설정('ko': 한글, 'en': 영어)

        Returns
        -------
        DataFrame or None
            작성자 정보
        """
        return self._to_info_DataFrame('d999006', lang=lang)

    def get_financial_statement_information(self, lang: str = 'ko') -> Union[DataFrame, None]:
        """ 재무제표 정보

        Parameters
        ----------
        lang: str
            표시 언어 설정('ko': 한글, 'en': 영어)

        Returns
        -------
        DataFrame
            제무제표 정보
        """
        return self._to_info_DataFrame('d999007', lang=lang)

    def exist_consolidated(self):
        """ 연결 재무제표 존재 여부를 확인하기 위한 함수

        Returns
        -------
        bool
            연결재무제표 존재시 True / 개별재무제표만 존재시 False
        """
        regex = re.compile(r'Consolidated', re.IGNORECASE)
        info_table = self.get_table_by_code('d999007')
        if info_table is None:
            raise ValueError("Missing consolidated financial statement information")
        cls_list = info_table.cls
        if not cls_list:
            # D999007에 fact가 없는 공시는 연결 재무상태표 Role 존재 여부로 판단
            return self.get_financial_statement(separate=False) is not None
        for cls in cls_list:
            titles = get_title(cls, 'en')
            for title in titles:
                if isinstance(title, str):
                    if regex.search(title):
                        return True
                else:
                    if regex.search(' '.join(title)):
                        return True
        return False

    def _get_statement_by_name(self, concept_id: str, separate: bool = False) -> Union[List[Table], None]:
        """ D999007 정보를 사용할 수 없을 때 Role 정의를 이용하여 재무제표를 검색하는 함수

        Parameters
        ----------
        concept_id: str
            dart-gcd_StatementOfFinancialPosition: 재무상태표
            dart-gcd_StatementOfComprehensiveIncome: 포괄손익계산서
            dart-gcd_StatementOfChangesInEquity: 자본변동표
            dart-gcd_StatementOfCashFlows: 현금프름표
        separate: bool, optional
            True: 개별재무제표
            False: 연결재무제표

        Returns
        -------
        list of Table or None
        """
        tables = self.get_table_by_name(DATASET_TITLE[concept_id], separate=separate)
        if tables is None:
            return None
        # 주석 Role(D851100 현금흐름표 주석 등)도 이름이 매칭되므로 본 재무제표 Role 번호로 필터링
        role_numbers = get_statement_role_numbers(separate=separate)
        tables = [table for table in tables
                  if table.code is not None and table.code.upper() in role_numbers]
        return tables if len(tables) > 0 else None

    def _get_statement(self, concept_id: str, separate: bool = False) -> Union[List[Table], None]:
        """ Financial statement information 을 이용하여 제공되는 재무제표를 추출하는 함수

        Parameters
        ----------
        concept_id: str
            dart-gcd_StatementOfFinancialPosition: 재무상태표
            dart-gcd_StatementOfComprehensiveIncome: 포괄손익계산서
            dart-gcd_StatementOfChangesInEquity: 자본변동표
            dart-gcd_StatementOfCashFlows: 현금프름표
        separate: bool, optional
            True: 개별재무제표
            False: 연결재무제표

        Returns
        -------
        Table or None
        """
        table = self.get_table_by_code('d999007')
        if table is None:
            return None
        table_dict = table.get_value_by_concept_id(concept_id)
        if not table_dict:
            # D999007 Role은 존재하나 fact가 없는 공시 존재 (ex. rcept_no 20250318001434)
            return self._get_statement_by_name(concept_id, separate=separate)
        compare_name = 'Separate' if separate else 'Consolidated'

        try:
            for keys, value in table_dict.items():
                for key in keys:
                    title = ''.join(key)
                    if re.search(compare_name, title, re.IGNORECASE):
                        code_list = consolidated_code_to_role_number(value, separate=separate)
                        tables = [self.get_table_by_code(code) for code in code_list]
                        return tables
        except KeyError:
            return self._get_statement_by_name(concept_id, separate=separate)
        return None

    def get_financial_statement(self, separate: bool = False) -> Union[List[Table], None]:
        """ 재무상태표(Statement of financial position)

        Parameters
        ----------
        separate: bool, optional
            개별(True) / 연결(False, 기본)

        Returns
        -------
        list of Table
            재무상태표 리스트
        """
        return self._get_statement('dart-gcd_StatementOfFinancialPosition', separate=separate)

    def get_income_statement(self, separate: bool = False) -> Union[List[Table], None]:
        """ 포괄손익계산서(Statement of comprehensive income)

        Parameters
        ----------
        separate: bool, optional
            개별(True) / 연결(False, 기본)

        Returns
        -------
        list of Table
            포괄손익계산서 리스트
        """
        return self._get_statement('dart-gcd_StatementOfComprehensiveIncome', separate=separate)

    def get_changes_in_equity(self, separate: bool = False) -> Union[List[Table], None]:
        """ 자본변동표(Statement of changes in equity	)

        Parameters
        ----------
        separate: bool, optional
            개별(True) / 연결(False, 기본)

        Returns
        -------
        list of Table
            자본변동표 리스트
        """
        return self._get_statement('dart-gcd_StatementOfChangesInEquity', separate=separate)

    def get_cash_flows(self, separate: bool = False) -> Union[List[Table], None]:
        """ 현금흐름표(Statement of cash flow)

        Parameters
        ----------
        separate: bool, optional
            개별(True) / 연결(False, 기본)

        Returns
        -------
        list of Table
            현금흐름표 리스트
        """
        return self._get_statement('dart-gcd_StatementOfCashFlows', separate=separate)

    def __repr__(self):
        df = self.get_document_information()
        if df is None:
            return ''
        columns = df.columns.tolist()
        dict_info = df.set_index(columns[1]).to_dict()
        info = None
        for key, value in dict_info.items():
            if key != 'label_ko':
                info = value
        return str(info)

    def _repr_html_(self):
        df = self.get_document_information()
        if df is None:
            return ''
        columns = df.columns.tolist()
        dict_info = df.set_index(columns[1]).to_dict()
        info = None
        header = None
        for key, value in dict_info.items():
            if key != 'label_ko':
                info = value
                keys = list(info.keys())
                header = ['', keys[0]]
                info.pop(keys[0])

        df = self.get_entity_information()
        columns = df.columns.tolist()
        df = df.drop(columns[0], axis=1).set_index(columns[1])
        info['Company name'] = df.loc['Entity iegistrant name'].iloc[0]  # Fix FutureWarning

        return dict_to_html(info, header=header)

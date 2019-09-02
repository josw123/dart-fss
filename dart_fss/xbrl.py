# -*- coding: utf-8 -*-
import re
import os, sys
import math
import datetime

import pandas as pd
from pandas import DataFrame

from typing import List, Union
from dateutil.relativedelta import relativedelta

from arelle.ModelXbrl import ModelXbrl
from arelle import Cntlr, XbrlConst

from dart_fss._utils import check_datetime, compare_str, dict_to_html, get_datetime
from dart_fss.regex import str_to_regex


def get_label_list(relationship_set, concepts, relationship=None):
    """ XBRL의 label list를 변환하는 함수 """
    if relationship is None:
        if len(relationship_set.modelRelationships) > 0:
            preferred = relationship_set.modelRelationships[0].preferredLabel
        else:
            preferred = None
    else:
        preferred = relationship.preferredLabel

    label_ko = concepts.label(lang='ko') if preferred is None \
        else concepts.label(preferredLabel=preferred, lang='ko')
    label_en = concepts.label(lang='en') if preferred is None \
        else concepts.label(preferredLabel=preferred, lang='en')

    res = {
        'concept_id': concepts.id,
        'order': 1.0 if relationship is None else relationship.order,
        'label_ko': label_ko,
        'label_en': label_en,
        'isAbstract': concepts.isAbstract,
        'children': []
    }

    new_relationship_set = relationship_set.fromModelObject(concepts)
    if len(new_relationship_set) > 0:
        new_relationship_set.sort(key=lambda x: x.order)
        for rel in new_relationship_set:
            new_concepts = rel.viewConcept
            res['children'].append(get_label_list(relationship_set, new_concepts, relationship=rel))
    return res


def flatten(tuple_list, res=None):
    """ 2차원 list를 1차원 리스트로 변환하는 함수 """
    results = list() if res is None else res
    for data in tuple_list:
        if isinstance(data, list):
            flatten(data, results)
        else:
            results.append(data)
    return results


def get_max_depth(labels, show_abstract=False):
    """ class의 최대 깊이를 확인하는 함수"""
    max_depth = 0

    if len(labels['children']) == 0 and labels['isAbstract'] is True:
        if show_abstract is True:
            return 1
        else:
            return 0

    for label in labels['children']:
        depth = get_max_depth(label, show_abstract=show_abstract)
        if max_depth < depth:
            max_depth = depth

    return 1 + max_depth


def get_title(cls, lang='ko'):
    """ cls에서 column의 title을 생성하는 함수 """
    title = []

    if cls['instant_datetime'] is None:
        start_date = cls['start_datetime'].strftime('%Y%m%d')
        end_date = cls['end_datetime'].strftime('%Y%m%d')
        title.append('{}-{}'.format(start_date, end_date))
    else:
        instant_date = cls['instant_datetime'].strftime('%Y%m%d')
        title.append('{}'.format(instant_date))
    qlist = []
    for qname in cls['label']:
        qlist.append(cls['label'][qname][lang].strip())
    title.append(tuple(qlist))
    return tuple(title)


def get_datetime_and_name(title):
    """ Column Title에서 날짜와 Tilte 명을 추출하는 함수"""
    regx = re.search(r'\[(.*?)\]', title, re.IGNORECASE)
    result = None
    if regx is not None:
        result = dict()
        instant_datetime = None
        start_datetime = None
        end_datetime = None

        datetime = regx.group(1).split(',')
        if len(datetime) == 1:
            instant_datetime = get_datetime(datetime[0])
        elif len(datetime) == 2:
            start_datetime = get_datetime(datetime[0])
            end_datetime = get_datetime(datetime[1])
        else:
            raise ValueError('Invalid date')

        name = re.sub(r'\[{}\]'.format(regx.group(1)), '', title)
        name = name.strip()

        result['instant_datetime'] = instant_datetime
        result['instant_date'] = start_datetime
        result['start_date'] = end_datetime
        result['name'] = name
    return result


def get_value_from_dataset(classification, dataset, concept_id):
    """ dataset에서 값을 추출하는 함수 """
    def str_to_float(val):
        try:
            return float(val)
        except ValueError:
            return val

    if isinstance(classification, dict):
        classification = [classification]

    results = list()
    added_title = list()
    for cls in classification:
        value = float('nan')
        for data in dataset[cls['cls_id']]:
            if compare_str(data.concept.id, concept_id):
                value = str_to_float(data.value)
                break
        title = get_title(cls, 'en')
        if title in added_title:
            index = added_title.index(title)
            if not math.isnan(value):
                results[index] = value
        else:
            results.append(value)
            added_title.append(title)
    return results


def generate_df_columns(definition, classification, max_depth, lang='ko', show_concept=True, show_class=True):
    """ Table의 DataFrame 변환시 Column Title 생성을 위한 함수"""
    columns = [(definition, 'concept_id')] if show_concept else []
    columns += [(definition, 'label_ko'), (definition, 'label_en')]

    if show_class:
        for idx in range(max_depth):
            columns.append((definition, 'class{}'.format(idx)))

    if isinstance(classification, dict):
        classification = [classification]

    added_title = list()
    for cls in classification:
        title = get_title(cls, lang)
        if title not in added_title:
            columns.append(title)
            added_title.append(title)
    return pd.MultiIndex.from_tuples(columns)


def generate_df_rows(labels, classification, dataset, max_depth,
                     lang="ko", parent=(), show_abstract=False,
                     show_concept=True, show_class=True):
    """ Table의 DataFrame으로 변환시 DataFrame의 Row 생성을 위한 함수"""
    lang_type = {
        'ko': 'label_ko',
        'en': 'label_en',
        'concepts': 'concept_id'
    }
    results = []
    new_parent = list(parent)
    new_parent.append(labels[lang_type[lang]])

    if show_class:
        if len(new_parent) > max_depth:
            return None

    row = None
    if not labels['isAbstract'] or show_abstract:
        row = [labels['concept_id']] if show_concept else []
        row += [labels['label_ko'], labels['label_en']]
        if show_class:
            for idx in range(max_depth):
                if idx < len(new_parent):
                    row.append(new_parent[idx])
                else:
                    row.append(None)
        row.extend(get_value_from_dataset(classification, dataset, labels['concept_id']))
        results.append(tuple(row))

    if len(labels['children']) > 0:
        for child in labels['children']:
            generated_row = generate_df_rows(child, classification, dataset, max_depth,
                                             lang=lang, parent=tuple(new_parent), show_abstract=show_abstract,
                                             show_concept=show_concept, show_class=show_class)
            if generated_row is not None:
                results.append(generated_row)
    else:
        return tuple(row) if row is not None else None

    return results


def consolidated_code_to_role_number(code, separate=False):
    """ 코드번호를 Role 번호로 변환하는 함수

    Parameters
    ----------
    code: str
        코드번호
    separate: bool, optional
        개별재무제표 여부

    Returns
    -------
    list of str
        Role 번호 리스트
    """
    consolidated_code = {
        'D1001': ['D210000'],
        'D1002': ['D220000'],
        'D2001': ['D431410'],
        'D2002': ['D431420'],
        'D2003': ['D432410'],
        'D2004': ['D432420'],
        'D2005': ['D310000', 'D410000'],
        'D2006': ['D310000', 'D420000'],
        'D2007': ['D320000', 'D410000'],
        'D2008': ['D320000', 'D420000'],
        'D2009': ['D310000'],
        'D2010': ['D320000'],
        'D3001': ['D610000'],
        'D4001': ['D510000'],
        'D4002': ['D520000'],
    }
    separated_code = {
        'D1001': ['D210005'],
        'D1002': ['D220005'],
        'D2001': ['D431415'],
        'D2002': ['D431425'],
        'D2003': ['D432415'],
        'D2004': ['D432425'],
        'D2005': ['D310005', 'D410005'],
        'D2006': ['D310005', 'D420005'],
        'D2007': ['D320005', 'D410005'],
        'D2008': ['D320005', 'D420005'],
        'D2009': ['D310005'],
        'D2010': ['D320005'],
        'D3001': ['D610005'],
        'D4001': ['D510005'],
        'D4002': ['D520005'],
    }
    return separated_code[code] if separate else consolidated_code[code]


def cls_datetime_check(cls, start_dt, end_dt):
    """ classification 의 시간이 시작일자와 종료일자 사이인지 체크하는 함수

    Parameters
    ----------
    cls: cls
        classification
    start_dt: str
        검색 시작 일자
    end_dt: str
        검색 종료 일자

    Returns
    -------
    bool
        시작일자와 종료일자 사이에 있을시 True / 아닐시 False

    """
    res = True
    instant_datetime = cls.get('instant_datetime')
    if instant_datetime:
        res = res and check_datetime(instant_datetime, start_dt, end_dt)
    start_datetime = cls.get('start_datetime')
    if start_datetime:
        res = res and check_datetime(start_datetime, start_dt, end_dt)
    end_datetime = cls.get('end_datetime')
    if end_datetime:
        res = res and check_datetime(end_datetime, start_dt, end_dt)
    return res


def cls_label_check(cls, query):
    """ classification label에 특정 단어가 포함된지 검색하는 함수

    Parameters
    ----------
    cls: cls
        classification
    query: str
        검색어

    Returns
    -------
    bool
        질의내용 포함시 True / 미포함시 False
    """
    if query is None:
        return True
    regex = str_to_regex(query)
    label = ''
    for qname in cls['label']:
        label = label + cls['label'][qname]['ko'] + cls['label'][qname]['en']
    if regex.search(label):
        return True
    return False


def cls_merge_type(classification):
    """ classification type이 2가지일 때 합쳐주는 함수

    Parameters
    ----------
    classification: cls
        classification 리스트

    Returns
    -------
    list of cls
        변환된 classification 리스트
    """
    cls_type = {'instant' if cls.get('instant_datetime') else 'not_instant' for cls in classification }

    if len(cls_type) == 2:
        for cls in classification:
            instant_datetime = cls.get('instant_datetime')
            if instant_datetime:
                year = instant_datetime.year
                start_datetime = datetime.datetime(year, 1, 1) # 해당년도 1월 1일로 설정
                end_datetime = instant_datetime
                cls['instant_datetime'] = None
                cls['start_datetime'] = start_datetime
                cls['end_datetime'] = end_datetime
    return classification


class Table(object):
    """ XBRL Table

        XBRL 파일에서 추출된 데이터를 기반으로 재무제표에 관한 정보를 담고 있는 클래스

       Attributes
       ----------
       parent: str
           로드한 파일 이름
       xbrl: ModelXbrl
           arelle Xbrl 클래스

       """
    def __init__(self, parent, xbrl, code, definition, uri):
        self.parent = parent
        self.code = code
        self.definition = definition
        self.uri = uri
        self._xbrl = xbrl
        self._facts = None
        self._dataset = None
        self._cls = None
        self._labels = None

    @property
    def facts(self):
        """list of modelFact: """
        if self._facts is None:
            arcrole = XbrlConst.parentChild
            relation = self._xbrl.relationshipSet(arcrole, self.uri)
            facts = []
            for fact in self._xbrl.facts:
                if relation.fromModelObject(fact.concept) \
                        or relation.toModelObject(fact.concept):
                    facts.append(fact)
            self._facts = facts
        return self._facts

    @property
    def dataset(self):
        """dict of modelFact: """
        if self._dataset is None:
            dataset = dict()
            for fact in self.facts:
                object_id = fact.context.objectId()
                if dataset.get(object_id) is None:
                    dataset[object_id] = []
                dataset[object_id].append(fact)

            self._dataset = dataset
        return self._dataset

    @property
    def cls(self):
        """classification 반환"""
        if self._cls is None:
            self._get_cls()
        return self._cls

    def cls_filter(self, start_dt=None, end_dt=None, label=None):
        """ classification 필터링 함수

        Parameters
        ----------
        start_dt: str
            검색 시작 일자
        end_dt: str
            검색 종료 일자
        label: str
            포함할 label 명

        Returns
        -------
        list of cls
            필터된 classification
        """
        return [item for item in self.cls
                if cls_datetime_check(item, start_dt, end_dt) and cls_label_check(item, label)]

    def _get_cls(self):
        """ classification 정보 추출 함수"""
        contexts = set()
        for data in self.facts:
            context = data.context
            contexts.add(context)

        cls = list()
        for context in contexts:
            object_id = context.objectId()

            # data가 없을때 무시
            if len(self.dataset[object_id]) < 1:
                continue

            instant_datetime = None
            start_datetime = None
            end_datetime = None
            if context.isInstantPeriod is True:
                instant_datetime = context.instantDatetime - relativedelta(days=1)

            else:
                start_datetime = context.startDatetime
                end_datetime = context.endDatetime - relativedelta(days=1)

            label = dict()
            dims = context.qnameDims
            if len(dims) > 0:
                for dimQname in sorted(dims.keys(), key=lambda d: str(d), reverse=True):
                    dim_value = dims[dimQname]
                    ko = dim_value.member.label(lang='ko')
                    ko = re.sub(r'\[.*?\]', '', ko)
                    en = dim_value.member.label(lang='en')
                    en = re.sub(r'\[.*?\]', '', en)
                    label[dimQname] = {
                        'ko': ko,
                        'en': en
                    }
            _cls = {
                'cls_id': object_id,
                'instant_datetime': instant_datetime,
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'label': label
            }
            cls.append(_cls)
        cls.sort(key=lambda x: x.get('instant_datetime') or x.get('start_datetime'), reverse=True)
        self._cls = cls
        return self._cls

    @property
    def labels(self):
        """labels 반환"""
        if self._labels is None:
            arcrole = XbrlConst.parentChild
            relationship_set = self._xbrl.relationshipSet(arcrole, self.uri)
            root_concept = relationship_set.rootConcepts[0]
            labels = get_label_list(relationship_set, root_concept)
            self._labels = labels
        return self._labels

    def to_DataFrame(self, cls=None, lang='ko', start_dt=None, end_dt=None,
                     label=None, show_abstract=False, show_class=True, show_depth=10,
                     show_concept=True, separator=True):
        """ Pandas DataFrame으로 변환하는 함수

        Parameters
        ----------
        cls: dict, optional
            classification
        lang: str, optional
            'ko' 한글 or 'en' 영문
        start_dt: str, optional
            검색 시작 일자
        end_dt: str, optional
            검색 종료 일자
        label: str, optional
            Column Label에 포함될 단어
        show_abstract: bool, optional
            abtract 표시 여부
        show_class: bool, optional
            class 표시여부
        show_depth: int, optional
            class 표시 깊이
        show_concept: bool, optional
            concept_id 표시 여부
        separator: bool, optional
            숫자 첫단위 표시 여부

        Returns
        -------
        DataFrame
            재무제표 DataFrame
        """
        if cls is None:
            cls = self.cls_filter(start_dt, end_dt, label)
        cls = cls_merge_type(cls)
        depth = get_max_depth(self.labels, show_abstract=show_abstract)
        depth = depth if depth < show_depth else show_depth

        table = self.parent.get_table_by_code('d999004')
        unit = get_value_from_dataset(table.cls, table.dataset, 'dart-gcd_EntityReportingCurrencyISOCode')

        definition = self.definition + ' (Unit: {})'.format(unit[0])
        columns = generate_df_columns(definition, cls, depth, lang,
                                      show_concept=show_concept, show_class=show_class)

        if separator:
            pd.options.display.float_format = '{:,}'.format
        else:
            pd.options.display.float_format = '{:}'.format
        df = pd.DataFrame(columns=columns)

        rows = generate_df_rows(self.labels, cls, self.dataset, depth, lang=lang,
                                show_abstract=show_abstract, show_concept=show_concept, show_class=show_class)
        data = flatten(rows)
        for idx, r in enumerate(data):
            df.loc[idx] = r

        regex_pass = str_to_regex('concept_id OR label_ko OR label_en OR class')
        df_count = df.count()
        drop_columns = []
        for key, count in df_count.items():
            if regex_pass.search(' '.join(key[1])):
                pass
            elif count <= 1:
                drop_columns.append(key)
        df = df.drop(drop_columns, axis=1)
        return df

    def get_value_by_concept_id(self, concept_id, start_dt=None, end_dt=None, label=None, lang='en'):
        """ concept_id을 이용하여 값을 찾아 주는 함수

        Parameters
        ----------
        concept_id: str
            재무제표 계정의 concept_id
        start_dt: str
            검색 시작 일자
        end_dt: str
            검색 종료 일자
        label: str
            검색 포함 label
        lang: str
            'ko' 한글 / 'en' 영문

        Returns
        -------
        dict of (str or float)
            { column 이름 : 값 }
        """
        cls = self.cls_filter(start_dt, end_dt, label)
        data = get_value_from_dataset(classification=cls, dataset=self.dataset, concept_id=concept_id)
        results = dict()
        for c, d in zip(cls, data):
            title = get_title(c, lang=lang)
            results[title] = d
        return results

    def __repr__(self):
        info = {
            'code': self.code,
            'definition': self.definition
        }
        return str(info)


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
            if compare_str(table.code, code):
                return table
        return None

    def _to_info_DataFrame(self, code: str, lang: str = 'ko') -> DataFrame:
        """ to_DataFrame wrapper

        Parameters
        ----------
        code: str
            Table Code
        lang: str
            'ko' or 'en'

        Returns
        -------
        DataFrame
            Pandas DataFrame
        """
        table = self.get_table_by_code(code)
        return table.to_DataFrame(lang=lang, show_class=False, show_concept=False, separator=False)

    def get_document_information(self, lang: str = 'ko') -> DataFrame:
        """ 공시 문서 정보

        Parameters
        ----------
        lang: str
            표시 언어 설정('ko': 한글, 'en': 영어)

        Returns
        -------
        DataFrame
            공시 문서 정보
        """
        return self._to_info_DataFrame('d999001', lang=lang)

    def get_period_information(self, lang: str = 'ko') -> DataFrame:
        """ 공시 문서 기간 정보

        Parameters
        ----------
        lang: str
            표시 언어 설정('ko': 한글, 'en': 영어)

        Returns
        -------
        DataFrame
            공시 문서 기간 정보
        """
        df = self._to_info_DataFrame('d999002', lang=lang)
        data = df[df.columns[2:]].iloc[3]
        data_set = [(key, data[key]) for key in data.keys()]
        new_columns = list(df.columns[:2]) + [data[0] for data in sorted(data_set, key=lambda x: x[1], reverse=True)]
        return df[new_columns]

    def get_audit_information(self, lang: str = 'ko') -> DataFrame:
        """ 감사 정보

        Parameters
        ----------
        lang: str
            표시 언어 설정('ko': 한글, 'en': 영어)

        Returns
        -------
        DataFrame
            감사 정보
        """
        return self._to_info_DataFrame('d999003', lang=lang)

    def get_entity_information(self, lang: str = 'ko') -> DataFrame:
        """ 공시 대상 정보

        Parameters
        ----------
        lang: str
            표시 언어 설정('ko': 한글, 'en': 영어)

        Returns
        -------
        DataFrame
            공시 대상 정보
        """
        return self._to_info_DataFrame('d999004', lang=lang)

    def get_entity_address_information(self, lang: str = 'ko') -> DataFrame:
        """ 주소 정보

        Parameters
        ----------
        lang: str
            표시 언어 설정('ko': 한글, 'en': 영어)

        Returns
        -------
        DataFrame
            주소 정보

        """
        return self._to_info_DataFrame('d999005', lang=lang)

    def get_author_information(self, lang: str = 'ko') -> DataFrame:
        """ 작성자 정보

        Parameters
        ----------
        lang: str
            표시 언어 설정('ko': 한글, 'en': 영어)

        Returns
        -------
        DataFrame
            작성자 정보
        """
        return self._to_info_DataFrame('d999006', lang=lang)

    def get_financial_statement_information(self, lang: str = 'ko') -> DataFrame:
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
        cls_list = info_table.cls
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

    def _get_statement(self, concept_id: str , separate: bool = False) -> Union[List[Table], None]:
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
        table_dict = table.get_value_by_concept_id(concept_id)
        compare_name = 'Separate' if separate else 'Consolidated'
        for keys, value in table_dict.items():
            for key in keys:
                title = ''.join(key)
                if re.search(compare_name, title, re.IGNORECASE):
                    code_list = consolidated_code_to_role_number(value, separate=separate)
                    tables = [self.get_table_by_code(code) for code in code_list]
                    return tables
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
        columns = df.columns.tolist()
        dict_info = df.set_index(columns[1]).to_dict()
        info = None
        for key, value in dict_info.items():
            if key != 'label_ko':
                info = value
        return str(info)

    def _repr_html_(self):
        df = self.get_document_information()
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
        info['Company name'] = df.loc['Entity iegistrant name'][0]

        return dict_to_html(info, header=header)


def get_xbrl_from_file(file_path: str) -> DartXbrl:
    """ XBRL 파일 로드 함수

    XBRL 파일을 로드하기 위한 함수로 로딩완료 후 DartXbrl 클래스를 반환한다

    Parameters
    ----------
    file_path: str
        XBRL 파일 경로

    Returns
    -------
    DartXbrl
        DartXbrl 클래스
    """
    # PyPI를 통해 설치된 Arelle 라이브러리 사용시 발생하는 오류 수정을 위한코드
    from .spinner import Spinner
    spinner = Spinner('XBRL Loading')
    spinner.start()

    if sys.platform == 'win32':
        pass
    elif sys.platform == 'darwin':
        arelle_app_dir = os.path.join(os.path.expanduser('~/Library/Application Support'), 'Arelle')
        if not os.path.exists(arelle_app_dir):
            os.makedirs(arelle_app_dir)
    else:
        arelle_app_dir = os.path.join(os.path.expanduser("~/.config"), "arelle")
        if not os.path.exists(arelle_app_dir):
            os.makedirs(arelle_app_dir)
    model_xbrl = Cntlr.Cntlr().modelManager.load(file_path)
    filename = file_path.split('\\')[-1]
    xbrl =  DartXbrl(filename, model_xbrl)
    spinner.stop()
    return xbrl

# -*- coding: utf-8 -*-
import re
import os, sys
import tempfile

import pandas as pd
from pandas import DataFrame

from typing import List, Union
from dateutil.relativedelta import relativedelta

from arelle.ModelXbrl import ModelXbrl
from arelle import Cntlr, XbrlConst

from ._utils import download_file, unzip, search_file, check_datetime, compare_str, dict_to_html, get_datetime


def get_label_list(relationship_set, concepts, relationship=None):
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
    results = list() if res is None else res
    for data in tuple_list:
        if isinstance(data, list):
            flatten(data, results)
        else:
            results.append(data)
    return results


def get_max_depth(labels, show_abstract=False):
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
    lang_type = {
        'ko': 'label_ko',
        'en': 'label_en',
        'concepts': 'label_en'
    }

    name = cls[lang_type[lang]]
    name = re.sub(r'\[.*?\]', '', name)
    name = name.strip()

    if cls['instant_datetime'] is None:
        start_date = cls['start_datetime'].strftime('%Y-%m-%d')
        end_date = cls['end_datetime'].strftime('%Y-%m-%d')
        title = '[{},{}]{}'.format(start_date, end_date, name)
    else:
        instant_date = cls['instant_datetime'].strftime('%Y-%m-%d')
        title = '[{}]{}'.format(instant_date, name)
    return title


def get_datetime_and_name(title):
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
    def str_to_float(val):
        try:
            return float(val)
        except ValueError:
            return val

    results = list()

    if isinstance(classification, dict):
        classification = [classification]

    for cls in classification:
        value = float('nan')
        for data in dataset[cls['cls_id']]:
            if compare_str(data.concept.id, concept_id):
                value = str_to_float(data.value)
                break
        results.append(value)

    return results


def generate_df_columns(classification, max_depth, lang='ko', show_concept=True, show_class=True):
    columns = ['concept_id'] if show_concept else []
    columns += ['label_ko', 'label_en']

    if show_class:
        for i in range(max_depth):
            columns.append('class{}'.format(i))

    if isinstance(classification, dict):
        classification = [classification]

    for cls in classification:
        title = get_title(cls, lang)
        columns.append(title)
    return columns


def generate_df_rows(labels, classification, dataset, max_depth,
                     lang="ko", parent=(), show_abstract=False,
                     show_concept=True, show_class=True):
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


class Table(object):

    def __init__(self, xbrl, code, definition, uri):
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
    def classification(self):
        if self._cls is None:
            self._cls = self.get_classification()
        return self._cls

    def get_classification(self, start_date=None, end_date=None, cls_type=None):
        contexts = set()
        for data in self.facts:
            contexts.add(data.context)

        cls = list()
        for context in contexts:
            object_id = context.objectId()
            if len(self.dataset[object_id]) < 2:
                continue

            instant_datetime = None
            start_datetime = None
            end_datetime = None
            if context.isInstantPeriod is True:
                instant_datetime = context.instantDatetime - relativedelta(days=1)
                if not check_datetime(instant_datetime, start_date, end_date):
                    continue

            else:
                start_datetime = context.startDatetime
                if not check_datetime(start_datetime, start_date, end_date):
                    continue
                end_datetime = context.endDatetime - relativedelta(days=1)
                if not check_datetime(end_datetime, start_date, end_date):
                    continue

            dims = context.qnameDims
            if len(dims) > 0:
                for dimQname in sorted(dims.keys(), key=lambda d: str(d)):
                    dim_value = dims[dimQname]

                    label_ko = dim_value.member.label(lang='ko')
                    label_en = dim_value.member.label(lang='en')

                    if cls_type is not None:
                        if re.search(cls_type, label_en + label_ko, re.IGNORECASE) is None:
                            continue
                    _cls = {
                        'cls_id': object_id,
                        'instant_datetime': instant_datetime,
                        'start_datetime': start_datetime,
                        'end_datetime': end_datetime,
                        'label_ko': label_ko,
                        'label_en': label_en
                    }
                    cls.append(_cls)
            else:
                if (instant_datetime or start_datetime or end_datetime) is not None:
                    _cls = {
                        'cls_id': object_id,
                        'instant_datetime': instant_datetime,
                        'start_datetime': start_datetime,
                        'end_datetime': end_datetime,
                        'label_ko': '',
                        'label_en': ''
                    }
                    cls.append(_cls)

        cls_tp_set = {'start' if x.get('instant_datetime') is None else 'instant' for x in cls}
        if len(cls_tp_set) == 2:

            def instant_to_start_end(value):
                if value['instant_datetime'] is not None:
                    value['end_datetime'] = value['instant_datetime']
                    value['start_datetime'] = get_datetime(value['instant_datetime']) - relativedelta(years=1)\
                                              + relativedelta(days=1)
                    value['instant_datetime'] = None
                return value

            def compare_class(cls1, cls2):
                for key1, key2 in zip(cls1, cls2):
                    if key1 == 'cls_id':
                        continue
                    if cls1[key1] != cls2[key2]:
                        return False
                return True

            cls = [instant_to_start_end(x) for x in cls]

            overlap = dict()

            overlap_index = []
            for idx, cls1 in enumerate(cls):
                is_overlap = False
                for cls2 in cls[idx+1:]:
                    if compare_class(cls1, cls2):
                        overlap[cls1['cls_id']] = cls2['cls_id']
                        is_overlap = True
                if is_overlap:
                    overlap_index.append(idx)

            new_cls = []
            for idx, _ in enumerate(cls):
                if idx not in overlap_index:
                    new_cls.append(cls[idx])
                else:
                    form_cls_id = cls[idx]['cls_id']
                    to_cls_id = overlap[form_cls_id]
                    self._dataset[to_cls_id] += self._dataset[form_cls_id]
            cls = new_cls

        cls.sort(key=lambda x: x.get('instant_datetime') or x.get('start_datetime'), reverse=True)
        return cls

    @property
    def labels(self):
        if self._labels is None:
            arcrole = XbrlConst.parentChild
            relationship_set = self._xbrl.relationshipSet(arcrole, self.uri)
            root_concept = relationship_set.rootConcepts[0]
            labels = get_label_list(relationship_set, root_concept)
            self._labels = labels
        return self._labels

    def to_Dataframe(self, cls=None, lang='ko', start_date=None, end_date=None,
                     title=None, show_abstract=False, show_class=True, show_depth=10,
                     show_concept=True, separator=True):
        if cls is None:
            cls = self.get_classification(start_date=start_date, end_date=end_date, cls_type=title)

        depth = get_max_depth(self.labels, show_abstract=show_abstract)
        depth = depth if depth < show_depth else show_depth
        columns = generate_df_columns(cls, depth, lang, show_concept=show_concept, show_class=show_class)

        if separator:
            pd.options.display.float_format = '{:,}'.format

        df = pd.DataFrame(columns=columns)

        rows = generate_df_rows(self.labels, cls, self.dataset, depth, lang=lang,
                                show_abstract=show_abstract, show_concept=show_concept, show_class=show_class)
        data = flatten(rows)
        for idx, r in enumerate(data):
            df.loc[idx] = r

        return df

    def get_value_by_concept_id(self, concept_id, start_date=None, end_date=None, cls_type=None, lang='en'):
        cls = self.get_classification(start_date=start_date, end_date=end_date, cls_type=cls_type)
        data = get_value_from_dataset(classification=cls, dataset=self.dataset, concept_id=concept_id)
        results = dict()
        for c, d in zip(cls, data):
            title = get_title(c, lang)
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
    def tables(self):
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
                tables.append(Table(self.xbrl, role_code, definition, uri))
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

    def _to_info_Dataframe(self, code: str, lang: str = 'ko') -> DataFrame:
        table = self.get_table_by_code(code)
        return table.to_Dataframe(lang=lang, show_class=False, show_concept=False, separator=False)

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
        return self._to_info_Dataframe('d999001', lang=lang)

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
        df = self._to_info_Dataframe('d999002', lang=lang)
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
        return self._to_info_Dataframe('d999003', lang=lang)

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
        return self._to_info_Dataframe('d999004', lang=lang)

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
        return self._to_info_Dataframe('d999005', lang=lang)

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
        return self._to_info_Dataframe('d999006', lang=lang)

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
        return self._to_info_Dataframe('d999007', lang=lang)

    def _get_statement(self, concept_id, separate=False):
        table = self.get_table_by_code('d999007')
        table_dict = table.get_value_by_concept_id(concept_id)
        compare_name = 'Separate' if separate else 'Consolidated'
        for key, value in table_dict.items():
            name = get_datetime_and_name(key).get('name', '')
            if compare_str(compare_name, name):
                code_list = consolidated_code_to_role_number(value, separate=separate)
                tables = [self.get_table_by_code(code) for code in code_list]
                return tables
        return None

    def get_financial_statement(self, separate: bool = False) -> List[Table]:
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

    def get_income_statement(self, separate: bool = False) -> List[Table]:
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

    def get_changes_in_equity(self, separate: bool = False) -> List[Table]:
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

    def get_cash_flows(self, separate: bool = False) -> List[Table]:
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
        dict_info = df.set_index('label_en').to_dict()
        info = None
        for key, value in dict_info.items():
            if key != 'label_ko':
                info = value
        return str(info)

    def _repr_html_(self):
        df = self.get_document_information()
        dict_info = df.set_index('label_en').to_dict()
        info = None
        header = None
        for key, value in dict_info.items():
            if key != 'label_ko':
                info = value
                keys = list(info.keys())
                header = ['', keys[0]]
                info.pop(keys[0])

        df = self.get_entity_information()
        df = df.drop('label_ko', axis=1).set_index('label_en')
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
    # Github 버전에서는 수정된 상태로 이후 삭제예정
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
    return DartXbrl(filename, model_xbrl)


def get_xbrl_from_website(url: str) -> List[DartXbrl]:
    """ Zip 파일로 압축된 XBRL 파일 로드 함수

    Parameters
    ----------
    url: str
        XBRL Zip 파일 주소

    Returns
    -------
    list of DartXbrl
        DartXbrl 클래스 리스트
    """
    xbrl_list = []
    with tempfile.TemporaryDirectory() as path:
        file_path = download_file(url, path)
        extract_path = unzip(file_path)
        xbrl_file = search_file(extract_path)
        for file in xbrl_file:
            xbrl = get_xbrl_from_file(file)
            xbrl_list.append(xbrl)
    return xbrl_list

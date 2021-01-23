# -*- coding: utf-8 -*-
import re
import math

import pandas as pd

from dart_fss.utils import check_datetime, str_compare,  get_datetime, get_currency_str, str_unit_to_number_unit
from dart_fss.utils.regex import str_to_regex


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


def get_value_from_dataset(classification, dataset, concept_id, label_ko=None, lang='ko',):
    """ dataset에서 값을 추출하는 함수 """
    def str_to_float(val):
        try:
            return float(val)
        except ValueError:
            return val

    if isinstance(classification, dict):
        classification = [classification]

    # XBRL 내부 주당이익에서 발생하는 오류 수정을 위한 코드
    currency_unit = None
    if label_ko is not None:
        regex = re.compile(r'\(단위:(.*)\)')
        unit = regex.search(label_ko)
        if unit is not None:
            unit = unit.group(0)
            currency = get_currency_str(unit)
            if currency is not None:
                currency_unit = str_unit_to_number_unit(currency)

    results = list()
    added_title = list()
    for cls in classification:
        value = float('nan')
        for data in dataset[cls['cls_id']]:
            if str_compare(data.concept.id, concept_id):
                value = str_to_float(data.value)
                # XBRL 내부 주당이익에서 발생하는 오류 수정을 위한 코드
                if currency_unit is not None:
                    decimals = str_to_float(data.decimals)
                    # decimals이 없을 경우 0으로 처리
                    if math.isinf(decimals) or math.isnan(decimals):
                        decimals = 0
                    value = value * pow(10, decimals)
                    value = value * currency_unit
                break

        title = get_title(cls, lang)
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
        row.extend(get_value_from_dataset(classification, dataset, labels['concept_id'],  labels['label_ko'], lang=lang))
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

    cls_datetime = {}

    for cls in classification:
        end_datetime = cls.get('end_datetime')
        start_datetime = cls.get('start_datetime')
        if end_datetime is not None:
            cls_datetime[end_datetime] = start_datetime

    if len(cls_datetime) > 0:
        for cls in classification:
            instant_datetime = cls.get('instant_datetime')
            if instant_datetime:
                cls['instant_datetime'] = None
                cls['start_datetime'] = cls_datetime[instant_datetime]
                cls['end_datetime'] = instant_datetime

    return classification

# -*- coding: utf-8 -*-
import re

import pandas as pd
from pandas import DataFrame

from dateutil.relativedelta import relativedelta

from arelle.ModelXbrl import ModelXbrl
from arelle import XbrlConst

from dart_fss.utils import str_to_regex
from dart_fss.xbrl.helper import (cls_label_check, get_label_list,
                                  cls_merge_type, cls_datetime_check,
                                  get_max_depth, get_value_from_dataset,
                                  generate_df_columns, generate_df_rows,
                                  flatten, get_title)


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
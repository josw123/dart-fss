import pandas as pd

from pandas import DataFrame
from typing import Dict, Optional

from dart_fss.utils import dict_to_html, create_folder


class FinancialStatement(object):
    """
    재무제표 검색 결과를 저장하는 클래스

    DART 공시 리포트들의 재무제표 검색 결과를 저장하고 있는 클래스로 검색 결과 및 검증을 위한 추출된 데이터의 Label을 확인할 수 있는 클래스


    Attributes
    ----------
    info: dict
        재무제표 검색 Parameters 값들
    """
    def __init__(self, statements: Dict[str, DataFrame], label_df: Dict[str, DataFrame], info: Dict[str, str]):
        if info.get('separator'):
            pd.options.display.float_format = '{:,}'.format
        else:
            pd.options.display.float_format = '{:}'.format
        self._statements = statements
        self._order = [tp for tp in self._statements]
        self._labels = label_df
        self.info = info

    @property
    def separator(self) -> bool:
        """ 1000 단위 구분점 표시 여부 """
        return self.info.get('separator', False)

    @separator.setter
    def separator(self, separator):
        """ 1000 단위 구분점 표시 여부 설정"""
        if separator:
            pd.options.display.float_format = '{:,}'.format
        else:
            pd.options.display.float_format = '{:}'.format
        self.info['separator'] = separator

    def show(self, tp, show_class: bool = True, show_depth: int = 10, show_concept: bool = True) -> Optional[DataFrame]:
        """
        재무제표 정보를 표시해주는 Method

        Parameters
        ----------
        tp: str
            표시할 재무제표 타입: 'fs' 재무상태표, 'is' 손익계산서, 'ci' 포괄손익계산서, 'cf' 현금흐름표
        show_class: bool
            class 표시 여부
        show_depth: bool
            표시할 class의 깊이
        show_concept: bool
            concept_id 표시 여부

        Returns
        -------
        DataFrame
            재무제표
        """
        from dart_fss.fs.extract import find_all_columns

        df = self._statements[tp]
        if df is None:
            return df
        class_columns = find_all_columns(df, 'class')

        if show_class is False:
            ncolumns = []
            columns = df.columns.tolist()
            for column in columns:
                if column not in class_columns:
                    ncolumns.append(column)
            if len(ncolumns) > 0:
                ncolumns = pd.MultiIndex.from_tuples(ncolumns)
            df = df[ncolumns]
        else:
            drop_rows = []
            columns = df.columns.tolist()
            cdf = df[class_columns]
            for idx in range(len(cdf)):
                for class_idx, item in enumerate(cdf.iloc[idx]):
                    if class_idx > show_depth and item is not None:
                        drop_rows.append(idx)
            ncolumns = []
            for column in columns:
                if column not in class_columns[show_depth + 1:]:
                    ncolumns.append(column)
            if len(ncolumns) > 0:
                ncolumns = pd.MultiIndex.from_tuples(ncolumns)
            df = df[ncolumns].drop(drop_rows)

        if show_concept is False:
            concept_colmuns = find_all_columns(df, 'concept_id')
            if len(concept_colmuns) == 1:
                ncolumns = []
                columns = df.columns.tolist()
                for column in columns:
                    if column not in concept_colmuns:
                        ncolumns.append(column)
                if len(ncolumns) > 0:
                    ncolumns = pd.MultiIndex.from_tuples(ncolumns)
                df = df[ncolumns]
        return df

    @property
    def labels(self) -> Dict[str, DataFrame]:
        """ 검색된 label들의 정보를 담고 있는 DataFrame """
        return self._labels

    def to_dict(self) -> Dict[str, str]:
        """ FinancialStatement의 요약 정보를 Dictionary 로 반환"""
        info = self.info
        df_info = []
        for tp in  self._order:
            df = self._statements.get(tp)
            if df is not None:
                df_info.append({'title': df.columns.tolist()[0][0]})
            else:
                df_info.append({'title': tp + ' is None'})
        info['financial statement'] = df_info
        return info

    def save(self, filename: str = None, path: str = None):
        """
        재무제표 정보를 모두 엑셀파일로 일괄저장

        Parameters
        ----------
        filename: str
            저장할 파일명(default: {corp_code}_{report_tp}.xlsx)
        path: str
            저장할 폴더(default: 실행폴더/fsdata)
        """
        import os
        if path is None:
            path = os.getcwd()
            path = os.path.join(path, 'fsdata')
            create_folder(path)

        if filename is None:
            filename = '{}_{}.xlsx'.format(self.info.get('corp_code'), self.info.get('report_tp'))

        file_path = os.path.join(path, filename)
        with pd.ExcelWriter(file_path) as writer:
            for tp in self._statements:
                fs = self._statements[tp]
                label = self._labels[tp]
                if fs is not None:
                    sheet_name = 'Data_' + tp
                    fs.to_excel(writer, sheet_name=sheet_name)
                    sheet_name = 'Labels_' + tp
                    label.to_excel(writer, sheet_name=sheet_name)
        return file_path

    def __getattr__(self, item):
        if item in self.info:
            return self.info[item]
        else:
            error = "'{}' object has no attribute '{}'".format(type(self).__name__, item)
            raise AttributeError(error)

    def __getitem__(self, item):
        if isinstance(item, str):
            return self._statements[item]
        else:
            return self._statements[self._order[item]]

    def __len__(self):
        return len(self._statements)

    def __repr__(self):
        from pprint import pformat
        info = self.to_dict()
        return pformat(info)

    def _repr_html_(self):
        return dict_to_html(self.to_dict(), header=['Label', 'Data'])
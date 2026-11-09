# -*- coding: utf-8 -*-
from pandas import DataFrame
from typing import List, Tuple


def dataframe_astype(df: DataFrame, columns: List[Tuple[str, type]]):
    """ DataFrame Column Type converter

    Parameters
    ----------
    df: DataFrame
        Pandas DataFrame
    columns: list of tuple of str, type
        column name and type for type conversion

    Returns
    -------
    DataFrame
        Pandas DataFrame
    """
    for column, tp in columns:
        if tp == int or tp == float:
            # 천 단위 구분자만 제거 (음수 부호 유지), 변환 실패 시('-' 등) 원본 유지
            converted = df[column].str.replace(',', '', regex=False).astype(tp, errors='ignore')
            if converted.dtype != df[column].dtype:
                df[column] = converted
        else:
            df[column] = df[column].astype(tp, errors='ignore')
    return df

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
            df[column] = df[column].str.replace(',|-', '').astype(tp, errors='ignore')
        else:
            df[column] = df[column].astype(tp, errors='ignore')
    return df

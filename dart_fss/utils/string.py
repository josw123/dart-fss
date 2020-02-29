import re


def str_compare(str1: str, str2: str) -> bool:
    """문자열 비교

    Parameters
    ----------
    str1: str
        string
    str2: str
        string

    Returns
    -------
    bool
        문자열이 동일하다면 True
    """
    str1 = str1.strip().lower()
    str2 = str2.strip().lower()
    return str1 == str2


def str_unit_to_number_unit(str_unit: str) -> int:
    """ 통화 단위를 숫자로 변화

    Parameters
    ----------
    str_unit: str
        통화 단위

    Returns
    -------
    int
        환산값
    """
    str_unit = re.sub(r'\s+', '', str_unit)
    str_unit_to_unit = {
        '억원': 100000000,
        '천만원': 10000000,
        '백만원': 1000000,
        '십만원': 100000,
        '만원': 10000,
        '천원': 1000,
        '백원': 100,
        '십원': 10,
        '원': 1,
        'USD': 1
    }
    return str_unit_to_unit[str_unit]


def str_insert_whitespace(word):
    return r'\s*'.join(word)


def str_upper(strings):
    if strings is None:
        return strings
    elif isinstance(strings, str):
        return strings.upper()
    elif isinstance(strings, list):
        return [x.upper() for x in strings]
    else:
        raise ValueError('invalid type')
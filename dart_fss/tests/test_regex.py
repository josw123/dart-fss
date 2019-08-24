from dart_fss.regex import str_to_regex


def test_str_to_regex():
    query = '삼성 OR ( 하이 AND 닉스)'
    regex = str_to_regex(query=query)
    actual = regex.search('하이닉')
    expected = None
    assert actual == expected


def test_str_to_regex_2():
    query = '삼성 OR 하이'
    regex = str_to_regex(query=query)
    actual = regex.search('삼성이닉스').group(0)
    expected = '삼성'
    assert  actual == expected

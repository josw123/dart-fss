from .._utils import dict_to_html, check_datetime


def test_dict_to_html():
    from bs4 import BeautifulSoup
    data = {
        'A': 1,
        'B': 2,
        'C': [{'D': 3}, {'E': 4}]
    }
    html = dict_to_html(data)
    soup = BeautifulSoup(html, 'html.parser')
    tr = soup.find_all('tr')
    sub_tr = tr[2].find_all('tr')

    actual = (len(tr), len(sub_tr))
    expected = (6, 3)

    assert actual == expected


def test_check_datetime():
    actual = check_datetime('20191231', '20190101', '20190201')
    expected = False
    assert actual == expected

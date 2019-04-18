from .._utils import dict_to_html


def test_dict_to_html():
    from bs4 import BeautifulSoup
    data = {
        'A': 1,
        'B': 2
    }
    html = dict_to_html(data)
    soup = BeautifulSoup(html, 'html.parser')
    tr = soup.find_all('tr')
    actual = set(x.find('th').text for x in tr)
    expected = set(x for x in data.keys())
    assert actual == expected

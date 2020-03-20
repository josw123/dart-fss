from dart_fss.api import info


def test_get_capital_increase():
    res = info.get_capital_increase('00126380', '2018', '11011')
    data = res['list'][0]
    actual = data.get('isu_dcrs_de')
    expected = '-'
    assert actual == expected


def test_get_chairman_individual_pay():
    res = info.get_chairman_individual_pay('00126380', '2018', '11011')
    actual = set(x.get('nm') for x in res['list'])
    expected = {'김현석', '고동진', '이상훈', '신종균', '윤부근', '김기남', '권오현'}
    assert len(actual.difference(expected)) == 0


def test_get_chairman_total_pay():
    res = info.get_chairman_total_pay('00126380', '2018', '11011')
    actual = res['list'][0].get('mendng_totamt')
    expected = '29,607,000,000'
    assert actual == expected


def test_get_dividend():
    res = info.get_dividend('00126380', '2018', '11011')
    actual = [x.get('lwfr') for x in res['list'] if x.get('se') == '주당액면가액(원)'][0]
    expected = '5,000'
    assert actual == expected


def test_get_employee():
    res = info.get_employee('00126380', '2018', '11011')
    actual = res['list'][0].get('rcept_no')
    expected = '20190401004781'
    assert actual == expected


def test_get_highest_salary_employee():
    res = info.get_highest_salary_employee('00126380', '2018', '11011')
    actual = [x.get('mendng_totamt') for x in res['list'] if x.get('nm') == '권오현'][0]
    expected = '7,034,000,000'
    assert actual == expected


def test_get_executive():
    res = info.get_executive('00126380', '2018', '11011')
    actual = [x.get('rgist_exctv_at') for x in res['list'] if x.get('nm') == '이상훈'][0]
    expected = '등기임원'
    assert actual == expected


def test_get_investment():
    res = info.get_investment('00126380', '2018', '11011')
    actual = [x.get('frst_acqs_de') for x in res['list'] if x.get('inv_prm') == '합계'][0]
    expected = '-'
    assert actual == expected


def test_get_major_shareholder():
    res = info.get_major_shareholder('00126380', '2018', '11011')
    actual = [x.get('bsis_posesn_stock_qota_rt') for x in res['list'] if x.get('bsis_posesn_stock_co') == '4,985,464'][0]
    expected = '3.86'
    assert actual == expected


def test_change_of_major_shareholder():
    res = info.change_of_major_shareholder('00126380', '2018', '11011')
    actual = res['list'][0].get('rm')
    expected = '-'
    assert actual == expected


def test_get_minority_shareholder():
    res = info.get_minority_shareholder('00126380', '2018', '11011')
    actual = res['list'][0].get('se')
    expected = '소액주주'
    assert actual == expected


def test_get_treasury_stock():
    res = info.get_treasury_stock('00126380', '2018', '11011')
    actual = res['list'][0].get('stock_knd')
    expected = '-'
    assert actual == expected




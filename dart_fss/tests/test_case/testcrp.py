import pytest
from dart_fss.corp import CorpList
from dart_fss.fs.extract import find_all_columns
from dart_fss.utils import str_compare


class TestCrp(object):
    corp_list = CorpList()

    def __init__(self, corp_code, bgn_de, separate, report_tp, end_de=None):
        corp = None
        if corp_code:
            corp = self.corp_list.find_by_corp_code(corp_code)
        else:
            pytest.fail('The parameter should be initialized: crp_cd or crp_nm')
        self.corp = corp
        self.bgn_de = bgn_de
        self.end_de = end_de
        self.separate = separate
        self.report_tp = report_tp
        self.test_set = []

    def add_test_value(self, fs_tp, date, column, item, expected):
        test_set = {
            'fs_tp': fs_tp,
            'date': date,
            'column': column,
            'item': item,
            'expected': expected
        }
        self.test_set.append(test_set)

    def run_test(self):
        fs = self.corp.extract_fs(bgn_de=self.bgn_de, end_de=self.end_de,
                                  separate=self.separate, report_tp=self.report_tp)
        for test in self.test_set:
            tp = test['fs_tp']
            date = test['date']
            column = test['column']
            item = test['item']
            expected = test['expected']

            df = fs[tp]
            date_column = find_all_columns(df=df, query=date)[0]
            label_column = find_all_columns(df=df, query=column)[0]

            actual = None

            for idx in range(len(df)):
                text = df[label_column].iloc[idx].replace(' ', '')
                if str_compare(text, item):
                    actual = df[date_column].iloc[idx]

            if actual != expected:
                pytest.fail("Test failed: corp_code='{}', ".format(self.corp.corp_code) +
                            "corp_name='{}', fs_tp='{}', ".format(self.corp.corp_name, tp) +
                            "start_dt='{}', report_tp='{}', ".format(self.bgn_de, fs.info['report_tp']) +
                            "date='{}', column='{}',".format(date, column) +
                            "item='{}', actual='{}', expected='{}'".format(item, actual, expected))


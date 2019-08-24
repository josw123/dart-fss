import re
import pytest
import dart_fss.crp as crp
from dart_fss._utils import compare_str
from dart_fss.fs_search import find_all_columns


class TestCrp(object):
    crp_list = crp.get_crp_list()

    def __init__(self, start_dt, separate, report_tp, crp_cd=None, crp_nm=None):
        crp = None
        if crp_cd:
            crp = self.crp_list.find_by_crp_cd(crp_cd)
        elif crp_nm:
            crp = self.crp_list.find_by_name(crp_nm)[0]
        else:
            pytest.fail('The parameter should be initialized: crp_cd or crp_nm')
        self.crp = crp
        self.start_dt = start_dt
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
        fs = self.crp.get_financial_statement(start_dt=self.start_dt, separate=self.separate, report_tp=self.report_tp)
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
                if compare_str(text, item):
                    actual = df[date_column].iloc[idx]

            if actual != expected:
                pytest.fail("Test failed: crp_cd='{}', fs_tp='{}', ".format(self.crp.crp_cd, tp) +
                            "start_dt='{}', report_tp='{}', ".format(self.start_dt, fs.info['report_tp']) +
                            "date='{}', column='{}',".format(date, column) +
                            "item='{}', actual='{}', expected='{}'".format(item, actual, expected))


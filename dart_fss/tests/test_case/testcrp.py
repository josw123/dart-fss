import re
import pytest
import dart_fss.crp as crp


class TestCrp(object):
    crp_list = crp.get_crp_list()

    def __init__(self, crp_cd=None, crp_nm=None):
        if crp_cd:
            crp = self.crp_list.find_by_crp_cd(crp_cd)
        elif crp_nm:
            crp = self.crp_list.find_by_name(crp_nm)[0]
        else:
            pytest.fail('The parameter should be initialized: crp_cd or crp_nm')
        self.crp = crp
        self.test_set = []

    def add_test_set(self, fs_tp, start_dt, test_tp, test_date, test_item, expected, report_tp='annual'):

        test_date = '{}-{}-{}'.format(test_date[:4], test_date[4:6], test_date[6:])

        test_set = {
            'fs_tp': fs_tp,
            'start_dt': start_dt,
            'test_tp': test_tp,
            'test_date': test_date,
            'test_item': test_item,
            'expected': expected,
            'report_tp': report_tp
        }
        self.test_set.append(test_set)

    def run_test(self):
        for data in self.test_set:
            start_dt = data['start_dt']
            fs_tp = data['fs_tp']
            test_tp = data['test_tp']
            test_date = data['test_date']
            test_item = data['test_item']
            expected = data['expected']
            report_tp = data['report_tp']
            df = self.crp.get_financial_statement(start_dt=start_dt,
                                                  fs_tp=fs_tp,
                                                  report_tp=report_tp)
            df[test_tp] = df[test_tp].str.replace(' ', '')
            df = df.set_index(test_tp)
            column = [col for col in df.columns if re.search(test_date, col)]
            if column:
                column = column[0]
            else:
                pytest.fail('Cannot find column - {}'.format(test_date))

            actual = df[column].loc[test_item]

            if actual != expected:
                pytest.fail('Test failed: crp_cd={}, fs_tp={}, '.format(self.crp.crp_cd, fs_tp) +
                            'start_dt={}, report_tp={}, '.format(start_dt, report_tp) +
                            'test_tp={}, test_data={}, '.format(test_tp, test_date) +
                            'test_item={}, expected={}, actual={}'.format(test_item, expected, actual))


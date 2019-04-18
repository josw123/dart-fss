import pytest
from .test_case.crp_case import test_crp_list


@pytest.mark.parametrize("crp", test_crp_list)
def test_crp_financial_statement(crp):
    crp.run_test()





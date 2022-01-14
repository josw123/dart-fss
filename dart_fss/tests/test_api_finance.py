# -*- coding: utf-8 -*-
from dart_fss.errors.errors import NoDataReceived


def test_fnltt_singl_acnt(dart):
    try:
        _ = dart.api.finance.fnltt_singl_acnt(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2018",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_fnltt_multi_acnt(dart):
    try:
        _ = dart.api.finance.fnltt_multi_acnt(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00356370,00126380",
            bsns_year="2018",
            reprt_code="11011",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_fnltt_singl_acnt_all(dart):
    try:
        _ = dart.api.finance.fnltt_singl_acnt_all(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00126380",
            bsns_year="2018",
            reprt_code="11011",
            fs_div="OFS",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_xbrl_taxonomy(dart):
    try:
        _ = dart.api.finance.xbrl_taxonomy(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            sj_div="BS1",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_download_xbrl(dart):
    import tempfile
    with tempfile.TemporaryDirectory() as temp:
        actual = dart.api.finance.download_xbrl(path=temp, rcept_no='20180402005019', reprt_code='11011')
        assert actual is not None

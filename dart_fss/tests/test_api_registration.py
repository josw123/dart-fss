# -*- coding: utf-8 -*-
from dart_fss.errors.errors import NoDataReceived


def test_extr_rs(dart):
    try:
        _ = dart.api.registration.extr_rs(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00219097",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_mg_rs(dart):
    try:
        _ = dart.api.registration.mg_rs(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00109718",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_stkdp_rs(dart):
    try:
        _ = dart.api.registration.stkdp_rs(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="01338724",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_bd_rs(dart):
    try:
        _ = dart.api.registration.bd_rs(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00858364",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_estk_rs(dart):
    try:
        _ = dart.api.registration.estk_rs(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00106395",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e


def test_dv_rs(dart):
    try:
        _ = dart.api.registration.dv_rs(
            api_key="xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx",
            corp_code="00105271",
            bgn_de="20190101",
            end_de="20191231",
        )
    except NoDataReceived:
        pass
    except Exception as e:
        raise e
